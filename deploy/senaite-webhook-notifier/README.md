# SENAITE → CTMS results-published notifier

A tiny host-side bridge that gives **near-instant** SENAITE → CTMS result syncing
*without* modifying SENAITE (no Plone add-on, no image rebuild).

## Why this exists

SENAITE/Plone has **no built-in outbound webhooks**. CTMS already exposes an
inbound webhook (`/api/v1/integrations/senaite/webhook/results-published/`,
authenticated with `X-SENAITE-Token`), and a 15-minute Celery-beat poll as a
fallback. This notifier closes the gap in between: it watches SENAITE's own JSON
API for newly **published** samples and calls the CTMS webhook for each one, so
results land in CTMS within ~1 minute of publishing instead of up to 15.

```
SENAITE (publish)  ──poll every 60s──►  notifier.py  ──POST X-SENAITE-Token──►  CTMS webhook  ──►  idempotent pull
```

CTMS does the real import (idempotent via Analysis UID), so duplicate or repeated
notifications are harmless.

## Files

| File | Purpose |
|------|---------|
| `notifier.py` | The script (Python 3 stdlib only — no `pip install`). |
| `senaite-webhook-notifier.env.example` | Config template (copy to `/etc/senaite-webhook-notifier.env`). |
| `senaite-webhook-notifier.service` | systemd oneshot unit that runs one poll. |
| `senaite-webhook-notifier.timer` | systemd timer that fires the service every 60s. |

## Install (systemd — recommended)

Run on the SENAITE host (or any box that can reach both SENAITE and CTMS):

```bash
# 1) Place the script
sudo mkdir -p /opt/senaite-webhook-notifier
sudo cp notifier.py /opt/senaite-webhook-notifier/

# 2) Config (fill in the password + secret; secret must equal CTMS SENAITE_WEBHOOK_SECRET)
sudo cp senaite-webhook-notifier.env.example /etc/senaite-webhook-notifier.env
sudo nano /etc/senaite-webhook-notifier.env
sudo chmod 600 /etc/senaite-webhook-notifier.env

# 3) Unprivileged service user + state dir
sudo useradd --system --no-create-home --shell /usr/sbin/nologin senaite-notifier || true
sudo mkdir -p /var/lib/senaite-webhook-notifier
sudo chown senaite-notifier:senaite-notifier /var/lib/senaite-webhook-notifier

# 4) SEED first so historical published samples are NOT re-sent
sudo -u senaite-notifier --preserve-env \
  env $(grep -v '^#' /etc/senaite-webhook-notifier.env | xargs) \
  python3 /opt/senaite-webhook-notifier/notifier.py --seed

# 5) Install + start the timer
sudo cp senaite-webhook-notifier.service /etc/systemd/system/
sudo cp senaite-webhook-notifier.timer   /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now senaite-webhook-notifier.timer

# 6) Verify
systemctl list-timers | grep senaite
journalctl -u senaite-webhook-notifier.service -f
```

## Install (cron alternative)

If you'd rather not use systemd:

```bash
# seed once (see step 4 above), then add to crontab:
* * * * * set -a; . /etc/senaite-webhook-notifier.env; set +a; \
  /usr/bin/python3 /opt/senaite-webhook-notifier/notifier.py \
  >> /var/log/senaite-notifier.log 2>&1
```

## Standalone loop (no cron/systemd)

For a quick trial or a container sidecar:

```bash
set -a; . /etc/senaite-webhook-notifier.env; set +a
python3 notifier.py --loop 60
```

## Testing

```bash
# Dry check that it reaches SENAITE + CTMS and finds published samples:
set -a; . /etc/senaite-webhook-notifier.env; set +a
python3 notifier.py --seed      # should log "recorded N published sample(s)"
# Publish a new sample in SENAITE, then within ~60s:
python3 notifier.py             # should log "notified CTMS for BLD-XXXX -> HTTP 200"
```

A `200` from CTMS means the webhook was accepted and an immediate pull was
dispatched. Confirm the result appears in CTMS **Laboratory** shortly after.

## Notes

- **State file** (`STATE_FILE`) records already-notified sample IDs so each
  publish fires exactly once. Deleting it (without `--seed`) would re-notify all
  currently-published samples — harmless (CTMS is idempotent) but noisy.
- **`CLIENT_TITLE`** scopes notifications to one SENAITE Client; leave blank for all.
- **Security:** the env file holds the SENAITE password and webhook secret —
  keep it `chmod 600` and out of git.
- This is the concrete implementation of gap #7 ("Native SENAITE outbound
  webhook") in `docs/SENAITE_Lab_Integration_Guide.md`.
```
