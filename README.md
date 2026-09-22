# DevSecOps Flask App

Small Flask + JWT app protected by a **GitHub Actions DevSecOps pipeline**
(SAST, SCA, secrets scan, container scan). Bad code fails the pipeline; clean
`master` goes green.

## Quick start

```bash
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # then edit real values — never commit .env
pytest --cov=app --cov-report=xml
python wsgi.py
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | yes | Flask secret (≥32 chars) |
| `JWT_SECRET_KEY` | yes | JWT signing key (≥32 chars) |
| `JWT_ACCESS_TOKEN_EXPIRES` | no | Seconds (default `900`) |
| `DATABASE_URL` | no | Default `sqlite:///app.db` (`/tmp` on Vercel) |

## API

- `GET /health` → `{"status":"ok"}`
- `POST /auth/register` → create user
- `POST /auth/login` → JWT access token
- `GET /auth/me` → current user (Bearer token)

## Pipeline (GitHub Actions)

Workflow: [`.github/workflows/devsecops.yml`](.github/workflows/devsecops.yml)

| Stage | Tool | Blocks? |
|-------|------|---------|
| Install & Test | pytest + coverage | yes |
| Secrets | Gitleaks | yes (any secret) |
| SAST | Semgrep + Bandit | yes (ERROR / HIGH+) |
| SCA | Trivy FS + pip-audit | yes (CRITICAL/HIGH) |
| Docker build & scan | Trivy image | yes (CRITICAL/HIGH) |
| Docker Hub push | docker | `master` only (if secrets set) |
| Vercel deploy | Vercel CLI | `master` only (if secrets set) |

Baseline (no security) for before/after comparison:
[`.github/workflows/as-is.yml`](.github/workflows/as-is.yml) — run manually.

### Demo branches (must fail)

| Branch | Fails at |
|--------|----------|
| `demo/leaked-secret` | Secrets (Gitleaks) |
| `demo/insecure-code` | SAST |
| `demo/vulnerable-dependency` | SCA |
| `demo/vulnerable-image` | Docker scan |

Never merge these into `master`.

### Local scans

```bash
make scan-local
```

## Docs

See `docs/` (French report, quality gates, manual GitHub secrets setup).
