# Deployment Notes

> Fill in every `TODO` with what you actually observed. Do not paste database URLs, passwords or other secrets into this file.

## Public URL

- Web service: TODO `https://model-review-board-XXXX.onrender.com`
- Health check: TODO `https://model-review-board-XXXX.onrender.com/health` returned `{"database": "ok", "status": "ok"}` with HTTP 200.

## Deployed Configuration

- Created from `render.yaml` as a Render Blueprint: one free Python web service (`model-review-board`) and one free PostgreSQL database (`model-review-db`), both in Frankfurt.
- `DATABASE_URL` comes from `fromDatabase.connectionString`, so Render injects the managed value at runtime and no credential was copied into the repository.
- The service starts with `flask --app app init-db`, which creates the `reviews` table in PostgreSQL if it is missing, then starts gunicorn.
- No Dockerfile. Render's native Python runtime builds the service with `pip install -r requirements.txt`.

## Persistence Evidence

1. TODO: Created review `TODO case reference` through the public URL at TODO time (UTC).
2. TODO: Triggered **Manual Deploy → Restart service** (or **Deploy latest commit**) at TODO time.
3. TODO: After the restart, the review was still on the dashboard with the same decision and notes.

Screenshots or log lines (optional): TODO

## Service Log Evidence

One successful request from the Render **Logs** tab (gunicorn access log):

```
TODO paste one line, e.g.  ... "GET /health HTTP/1.1" 200 ...
```

## Observed Limitation

TODO: describe one limitation you saw. For example: the free web service spins down after about 15 minutes without traffic, so the first request afterwards took about TODO seconds while it started again. Free Render PostgreSQL databases also expire 30 days after creation unless upgraded.

## Cleanup and Cost Awareness

- Plan used: Free (web service) and Free (PostgreSQL). Expected cost: 0.
- TODO choose one:
  - [ ] Removed: deleted the web service and the database in the Render dashboard on TODO date. Confirmed both are gone from the dashboard.
  - [ ] Intentionally retained until TODO date for grading. They will be deleted after that. The free database expires on TODO date in any case.

## Reflection

**Why SQLite locally but not on Render.** A SQLite database is a single file next to the app. That makes it ideal for development: no server to install, no cloud account, and it can be deleted and recreated in seconds. A free Render web service, however, has an ephemeral filesystem. Every deploy, restart or spin-down starts the service from a fresh copy of the build, so any SQLite file written at runtime is lost, together with every review. It would also break as soon as the service ran more than one instance, because each instance would have its own file. PostgreSQL runs as a separate managed service, so the data outlives any restart of the web service and every instance sees the same records.

**One change needed before handling sensitive production review data.** The app has no authentication: anyone with the URL can read, change or delete any review. Before handling sensitive data it would need reviewer login (for example single sign-on through the company identity provider), with access limited to the review team, plus CSRF protection on all POST forms so another site cannot submit actions on a logged-in reviewer's behalf.
