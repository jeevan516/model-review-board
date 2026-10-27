# Deployment Notes

> Fill in every `TODO` with what you actually observed. Do not paste database URLs, passwords or other secrets into this file.

## Public URL

- Web service: `https://model-review-board.onrender.com`
- Health check: `https://model-review-board.onrender.com/health` returned `{"database": "ok", "status": "ok"}` with HTTP 200.

## Deployed Configuration

- Created from `render.yaml` as a Render Blueprint: one free Python web service (`model-review-board`) and one free PostgreSQL database (`model-review-db`), both in Frankfurt.
- `DATABASE_URL` comes from `fromDatabase.connectionString`, so Render injects the managed value at runtime and no credential was copied into the repository.
- The service starts with `flask --app app init-db`, which creates the `reviews` table in PostgreSQL if it is missing, then starts gunicorn.
- No Dockerfile. Render's native Python runtime builds the service with `pip install -r requirements.txt`.

## Persistence Evidence

1. Created review `RENDER-TEST-001` through the public URL at 17:10 on 27 Oct 2026 (UTC).
2. Triggered **Manual Deploy → Restart service** at 17:12 on 27 Oct 2026 (UTC).
3. After the restart, the review was still on the dashboard at `/reviews/1` with the same decision (Pending), prediction (NA), confidence (1.00) and created time (27 Oct 2026, 17:10).

## Service Log Evidence

One successful request from the Render **Logs** tab (gunicorn access log):

```
10.216.27.223 - - [27/Oct/2026:17:04:52 +0000] "GET /health HTTP/1.1" 200 32 "-" "Render/1.0"
```

## Observed Limitation

The free web service spins down after about 15 minutes without outside traffic. The last outside request was around 17:20 UTC, and at 17:35:54 UTC the logs showed gunicorn being stopped (`Handling signal: term`, then `Shutting down: Master`). Render's own `/health` checks every 5 seconds did not keep it awake. The next visit woke the service, and the dashboard loaded in just under 5 seconds, quicker than the 30–60 seconds Render warns about, but still a noticeable wait compared with an always-on service. Free Render PostgreSQL databases also expire 30 days after creation unless upgraded.

## Cleanup and Cost Awareness

- Plan used: Free (web service) and Free (PostgreSQL). Expected cost: 0.
- [x] Intentionally retained for grading so the public URL can be checked. Both the web service and the database will be deleted from the Render dashboard once grading is finished, and no later than 26 Nov 2026. The free database was created on 27 Oct 2026 and expires on 26 Nov 2026 in any case.

## Reflection

**Why SQLite locally but not on Render.** A SQLite database is a single file next to the app. That makes it ideal for development: no server to install, no cloud account, and it can be deleted and recreated in seconds. A free Render web service, however, has an ephemeral filesystem. Every deploy, restart or spin-down starts the service from a fresh copy of the build, so any SQLite file written at runtime is lost, together with every review. It would also break as soon as the service ran more than one instance, because each instance would have its own file. PostgreSQL runs as a separate managed service, so the data outlives any restart of the web service and every instance sees the same records.

**One change needed before handling sensitive production review data.** The app has no authentication: anyone with the URL can read, change or delete any review. Before handling sensitive data it would need reviewer login (for example single sign-on through the company identity provider), with access limited to the review team, plus CSRF protection on all POST forms so another site cannot submit actions on a logged-in reviewer's behalf.
