# ============================================================
# MalipoHub — production image
# Target: 256 MB RAM / 0.25 vCPU Hobby plan
# ============================================================
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_APP=app.py \
    PORT=8000

WORKDIR /app

# System deps kept minimal — psycopg2-binary needs libpq at runtime only
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 curl \
 && rm -rf /var/lib/apt/lists/*

# Layer 1: dependencies only (best cache reuse)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Layer 2: application code
COPY . .

# Non-root user
RUN useradd --create-home --shell /bin/bash appuser \
 && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Container-level healthcheck (platform may ignore, but harmless)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:${PORT}/ || exit 1

# Tuned for 0.25 vCPU / 256 MB:
#   1 sync worker, 2 threads  → ~90–120 MB resident
#   timeout 120               → survives slow DB cold start
#   access log to stdout      → visible in platform logs
CMD ["sh", "-c", "gunicorn app:app \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 1 \
  --threads 2 \
  --timeout 120 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --max-requests 500 \
  --max-requests-jitter 50 \
  --access-logfile - \
  --error-logfile -"]