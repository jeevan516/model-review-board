# Model Review Board: Flask + gunicorn, same start command as render.yaml.
# Build:  docker compose build      (or: docker build -t model-review-board .)
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

# Run as a non-root user; instance/ holds the SQLite file when DATABASE_URL is unset.
RUN useradd --create-home appuser && mkdir -p /app/instance && chown appuser /app/instance
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=5 --start-period=10s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)"

# init-db only creates missing tables, so it is safe on every start.
CMD ["sh", "-c", "flask --app app init-db && exec gunicorn 'app:create_app()' --bind 0.0.0.0:${PORT} --access-logfile -"]
