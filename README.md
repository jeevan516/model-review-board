# Model Review Board

A small Flask app where an ML team reviews model predictions before another department uses them. Reviews are stored in one relational table: SQLite locally, PostgreSQL on Render.

## Run Locally (no cloud account needed)

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements-dev.txt

copy .env.example .env          # optional, the defaults work without it
flask --app app init-db         # creates instance/reviews.db
flask --app app seed-db         # optional: adds 3 sample reviews
flask --app app run --debug
```

Open http://127.0.0.1:5000.

Plain `python -m venv .venv` and `pip install -r requirements-dev.txt` work too.

## Tests

```powershell
pytest
```

The tests cover the dashboard, validation, editing, deletion and the health check, using an in-memory SQLite database.

## Routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Dashboard with all reviews and status totals |
| GET, POST | `/reviews/new` | Create a review |
| GET | `/reviews/<id>` | Read one review |
| GET, POST | `/reviews/<id>/edit` | Change the decision, notes or other fields |
| GET | `/reviews/<id>/delete` | Delete confirmation page (does not delete) |
| POST | `/reviews/<id>/delete` | Delete the review |
| GET | `/health` | `200` if the database answers, `503` if not |

## Configuration

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///reviews.db` (in `instance/`) | Render sets this from the managed database. `postgres://` and `postgresql://` URLs are rewritten to use the psycopg 3 driver. |
| `SECRET_KEY` | development-only value | Signs flash messages. Render generates a random value. |

`.env`, `instance/` and `*.db` files are git-ignored.

## Deploy to Render

1. Push this repository to GitHub.
2. In Render, choose **New → Blueprint** and select the repository. Render reads [render.yaml](render.yaml) and creates the web service and the PostgreSQL database, wiring `DATABASE_URL` between them.
3. When the deploy finishes, open the service URL and `/health`.
4. Record the evidence in [reports/deployment-notes.md](reports/deployment-notes.md).

Free Render services spin down when idle, and free databases expire after 30 days. Delete both from the Render dashboard when you no longer need them.
