# UAT Feedback (temporary)

An in-app feedback channel for **User Acceptance Testing**. Users click a
floating **Feedback** button on any page, write a Bug/Question/Suggestion, and
optionally attach a **screenshot** of the current page (captured in the browser
with `html2canvas`). Submissions are stored in the HACT database — the
screenshot as a file under `MEDIA_ROOT/feedback/` — so **no clinical data leaves
the platform** to any third-party service.

- **Backend:** `backend/feedback/` app → `POST /api/v1/feedback/items/`
- **Frontend:** `frontend/src/components/FeedbackWidget.jsx`, mounted in
  `DashboardLayout` and `EdcLayout`.
- **Review:** Django admin → *User Feedback (UAT) → Feedback items* (screenshot
  preview, filters, status/notes). Only `admin`/`study_admin` can list/manage via
  the API; **any authenticated user can submit**.

## Who can do what
| Action | Roles |
|--------|-------|
| Submit feedback (+screenshot) | any authenticated user |
| List / review / download screenshot / delete (API) | `study_admin`, `admin` (+ Django admin superusers) |

## Turn it OFF instantly (no code removal)
Set both flags and redeploy:
- Backend env: `UAT_FEEDBACK_ENABLED=false`  → API routes 404.
- Frontend build env: `VITE_UAT_FEEDBACK=false` → the button is hidden.

## Full removal after UAT
1. **Frontend**
   - Remove `<FeedbackWidget />` and its import from
     `frontend/src/layouts/DashboardLayout.jsx` and `frontend/src/layouts/EdcLayout.jsx`.
   - Delete `frontend/src/components/FeedbackWidget.jsx`.
   - Remove the `FEEDBACK` entry from `frontend/src/api/endpoints.js`.
   - `npm remove html2canvas-pro` (optional — only used here).
2. **Backend**
   - Remove `"feedback.apps.FeedbackConfig"` from `HACT_APPS` and the
     `UAT_FEEDBACK_ENABLED` line in `backend/hact_ctms/settings.py`.
   - Remove the feedback `path(...)` include in `backend/hact_ctms/urls.py`
     (and the `from django.conf import settings` import if now unused).
   - Drop the table + delete the app:
     ```bash
     python manage.py migrate feedback zero   # drops feedback_items
     ```
     then delete the `backend/feedback/` directory.
   - (Optional) delete `MEDIA_ROOT/feedback/` screenshot files.
3. Export anything worth keeping first (Django admin, or the API list) — e.g. a
   CSV of feedback for the UAT report.

> This feature is intentionally self-contained so it can be deleted in minutes
> without touching any clinical/study code.
