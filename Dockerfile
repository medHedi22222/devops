# Multi-stage Dockerfile for Flask application
# - Pinned base image (no :latest)
# - Non-root runtime user
# - No secrets baked into the image (inject at runtime via --env-file / orchestrator)
# - HEALTHCHECK against /health

# ---------------------------------------------------------------------------
# Stage 1: build / install Python dependencies
# ---------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install into an isolated prefix so we can copy it cleanly to the runtime image
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2: minimal runtime image
# ---------------------------------------------------------------------------
FROM python:3.11-slim-bookworm

WORKDIR /app

# curl is required for HEALTHCHECK; keep the image lean otherwise
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed packages from builder into system paths
COPY --from=builder /install /usr/local

# Application code only (no .env, no tests — see .dockerignore)
COPY app/ ./app/
COPY wsgi.py .

RUN mkdir -p /app/instance \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1:5000/health || exit 1

# Secrets must be provided at runtime (e.g. docker run --env-file .env)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "wsgi:app"]
