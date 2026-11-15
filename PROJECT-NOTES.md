# Model Review Board: project notes

_Last updated: 15 Nov 2026_

## Project
**Model Review Board.** A small Flask web app where an ML team reviews model predictions
before another department uses them. Reviews are stored in one relational table:
SQLite locally, PostgreSQL in production.

- **Goal:** build a full CRUD web app, test it, and deploy it with a managed database
  (Render), then run it in Docker too.

## Approach
1. **App:** Flask + Flask-SQLAlchemy; dashboard with status totals, create / read / edit /
   delete reviews, search, filter tabs and status charts; `/health` checks the database.
2. **Config:** `DATABASE_URL` (default local SQLite) and `SECRET_KEY` from the environment;
   `postgres://` URLs rewritten for the psycopg 3 driver.
3. **Tests:** pytest with an in-memory SQLite database for dashboard, validation, editing,
   deletion and the health check.
4. **Deploy to Render:** `render.yaml` blueprint: free web service + free PostgreSQL, the
   connection string injected by Render (no secret in the repo).
5. **Docker:** `Dockerfile` + `docker-compose.yaml` (app + Postgres 17, same start command
   as Render), and a Portainer stack on http://localhost:5050.

## Results
| Check | Result |
|---|---|
| Test suite | **29 / 29 pass** |
| Render deployment | `/health` returned `{"database": "ok", "status": "ok"}` (HTTP 200) |
| Persistence | review `RENDER-TEST-001` survived a service restart (27 Oct 2026) |
| Free-plan limit | spins down after ~15 min idle; woke in just under 5 s |
| Docker / Portainer | `/health` and `/` return 200 with the Postgres container |

## Future engineering
- Reviewer login (single sign-on) so only the review team can read or change reviews.
- CSRF protection on every POST form.
- Database migrations (Alembic) instead of `create_all()`.
- CI on every pull request; move off the free Render database before it expires (26 Nov 2026).

## Update log
- 27 Oct 2026: deployed to Render, persistence and log evidence recorded.
- 15 Nov 2026: Dockerfile, compose file and Portainer stack added; PR #1.
