#!/usr/bin/env python3
"""
SENAITE -> CTMS results-published notifier (host-side bridge).

SENAITE/Plone has no built-in outbound webhooks, so this lightweight script runs
on the SENAITE host (or any box that can reach both SENAITE and CTMS), polls
SENAITE's JSON API for newly *published* AnalysisRequests, and calls the CTMS
inbound webhook for each new one. CTMS then performs the actual (idempotent)
pull. Run it every ~60s via a systemd timer or cron for near-instant syncing.

Stdlib only — no pip install required. Config comes from environment variables
(see senaite-webhook-notifier.env.example).

Environment variables
----------------------
  SENAITE_API_URL         Base of SENAITE JSON API.
                          e.g. https://ctms.hacts.org/senaite/@@API/senaite/v1
  SENAITE_API_USER        SENAITE member with permission to view samples.
  SENAITE_API_PASSWORD    That member's password.
  CTMS_WEBHOOK_URL        CTMS inbound webhook.
                          e.g. https://ctms.hacts.org/api/v1/integrations/senaite/webhook/results-published/
  SENAITE_WEBHOOK_SECRET  Shared secret; sent as the X-SENAITE-Token header.
  CLIENT_TITLE            (optional) Only notify samples under this SENAITE Client.
  STATE_FILE              (optional) Where to persist already-notified sample IDs.
                          Default: ./senaite_notifier_state.json
  LIMIT                   (optional) Max published samples to scan per run (default 200).
  VERIFY_TLS              (optional) '0' to skip TLS verification (self-signed). Default '1'.

Usage
-----
  python3 notifier.py            # one poll cycle (for cron / systemd timer)
  python3 notifier.py --seed     # record current published samples WITHOUT
                                  # notifying (run once at install so history
                                  # isn't re-sent), then exit
  python3 notifier.py --loop 60  # run forever, polling every 60s (no cron needed)
"""
import argparse
import base64
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"{ts} senaite-notifier: {msg}", flush=True)


def _env(name, default=None, required=False):
    val = os.environ.get(name, default)
    if required and not val:
        log(f"FATAL: required env var {name} is not set")
        sys.exit(2)
    return val


def _ssl_ctx():
    if _env("VERIFY_TLS", "1") == "0":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return None


def _basic_auth_header(user, password):
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return f"Basic {token}"


def fetch_published_ids(api_url, user, password, client_title, limit):
    """Return list of {'id', 'client'} for AnalysisRequests in review_state=published."""
    params = {
        "portal_type": "AnalysisRequest",
        "review_state": "published",
        "sort_on": "modified",
        "sort_order": "descending",
        "limit": str(limit),
        "complete": "yes",
    }
    if client_title:
        params["getClientTitle"] = client_title
    url = api_url.rstrip("/") + "/search?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Authorization": _basic_auth_header(user, password),
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20, context=_ssl_ctx()) as resp:
        data = json.loads(resp.read().decode())
    out = []
    for it in data.get("items", []):
        sid = it.get("id")
        if sid:
            out.append({"id": sid, "client": it.get("getClientTitle", "")})
    return out


def notify_ctms(webhook_url, secret, sample_id):
    body = json.dumps({"senaite_sample_id": sample_id, "status": "published"}).encode()
    req = urllib.request.Request(webhook_url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-SENAITE-Token": secret,
    })
    with urllib.request.urlopen(req, timeout=20, context=_ssl_ctx()) as resp:
        return resp.status, resp.read().decode()[:300]


def load_state(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return set(json.load(f).get("notified", []))
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return set()


def save_state(path, notified):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"notified": sorted(notified),
                   "updated": datetime.now(timezone.utc).isoformat()}, f, indent=2)
    os.replace(tmp, path)  # atomic


def run_once(cfg, seed=False):
    notified = load_state(cfg["state_file"])
    try:
        samples = fetch_published_ids(
            cfg["api_url"], cfg["user"], cfg["password"], cfg["client_title"], cfg["limit"]
        )
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        log(f"ERROR fetching published samples from SENAITE: {e}")
        return 1

    current = {s["id"] for s in samples}
    new_ids = [s["id"] for s in samples if s["id"] not in notified]

    if seed:
        notified |= current
        save_state(cfg["state_file"], notified)
        log(f"SEED: recorded {len(current)} published sample(s) without notifying. "
            f"Future runs will only notify newly-published samples.")
        return 0

    if not new_ids:
        log(f"no new published samples ({len(current)} known).")
        return 0

    ok = 0
    for sid in new_ids:
        try:
            code, snippet = notify_ctms(cfg["webhook_url"], cfg["secret"], sid)
            if 200 <= code < 300:
                notified.add(sid)
                ok += 1
                log(f"notified CTMS for {sid} -> HTTP {code}")
            else:
                log(f"CTMS rejected {sid} -> HTTP {code}: {snippet}")
        except urllib.error.HTTPError as e:
            log(f"CTMS HTTP error for {sid} -> {e.code}: {e.read().decode()[:200]}")
        except (urllib.error.URLError, TimeoutError) as e:
            log(f"CTMS unreachable for {sid}: {e}")

    save_state(cfg["state_file"], notified)
    log(f"done: {ok}/{len(new_ids)} new sample(s) notified.")
    return 0 if ok == len(new_ids) else 1


def build_cfg():
    return {
        "api_url": _env("SENAITE_API_URL", required=True),
        "user": _env("SENAITE_API_USER", required=True),
        "password": _env("SENAITE_API_PASSWORD", required=True),
        "webhook_url": _env("CTMS_WEBHOOK_URL", required=True),
        "secret": _env("SENAITE_WEBHOOK_SECRET", required=True),
        "client_title": _env("CLIENT_TITLE", ""),
        "state_file": _env("STATE_FILE", os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "senaite_notifier_state.json")),
        "limit": int(_env("LIMIT", "200")),
    }


def main():
    ap = argparse.ArgumentParser(description="SENAITE -> CTMS results-published notifier")
    ap.add_argument("--seed", action="store_true",
                    help="record current published samples without notifying, then exit")
    ap.add_argument("--loop", type=int, metavar="SECONDS", default=0,
                    help="run forever, polling every N seconds (omit for a single run)")
    args = ap.parse_args()
    cfg = build_cfg()

    if args.seed:
        sys.exit(run_once(cfg, seed=True))

    if args.loop > 0:
        log(f"starting loop mode, polling every {args.loop}s. api={cfg['api_url']}")
        while True:
            run_once(cfg)
            time.sleep(args.loop)
    else:
        sys.exit(run_once(cfg))


if __name__ == "__main__":
    main()
