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
| DAST | OWASP ZAP | yes (HIGH/CRITICAL) |
| Deploy | Vercel GitHub integration | automatic after a push to `master` |

Baseline (no security) for before/after comparison:
[`.github/workflows/as-is.yml`](.github/workflows/as-is.yml) — run manually.

### Demo branches (must fail)

| Branch | Fails at |
|--------|----------|
| `demo/leaked-secret` | Secrets (Gitleaks) |
| `demo/insecure-code` | SAST |
| `demo/vulnerable-dependency` | SCA |

Never merge these into `master`.

### Local scans

```bash
make scan-local
```

## Pre-commit Hooks (Shift-Left Security)

Pre-commit hooks run security checks **before** you commit, catching issues early (shift-left security).

### Installation

```bash
# Install pre-commit framework
pip install pre-commit

# Install hooks from .pre-commit-config.yaml
pre-commit install

# Run hooks on all files (manual)
pre-commit run --all-files
```

### Hooks Included

| Hook | Purpose | Blocks? |
|------|---------|---------|
| Gitleaks | Detects secrets (API keys, passwords) | yes |
| Bandit | Python security linter (SQL injection, XSS, etc.) | yes |
| Semgrep | Custom security rules (OWASP Top 10) | yes |
| Black | Python code formatter | auto-fix |
| Flake8 | Python style guide | warning |
| detect-private-key | Detects private keys | yes |
| check-added-large-files | Prevents large file commits | yes |

### How It Works

When you run `git commit`, pre-commit automatically:
1. Scans staged files for secrets (Gitleaks)
2. Runs Python security checks (Bandit, Semgrep)
3. Formats code (Black)
4. Checks for common issues

If any security issue is found, the commit is **blocked** until fixed.

## IDE Security Extensions (Developer Security)

Install these extensions in your IDE for real-time security feedback:

### VS Code Extensions

1. **SonarLint** - Real-time code quality and security (coupled to SonarQube)
   - Extension ID: `sonarsource.sonarlint-vscode`
   - Detects: Code smells, bugs, vulnerabilities

2. **Python** (Microsoft) - Built-in linting with security
   - Extension ID: `ms-python.python`
   - Enable: Pylint, Flake8, Bandit

3. **ESLint** (for any JS/TS in project)
   - Extension ID: `dbaeumer.vscode-eslint`
   - Config: Security rules enabled

4. **Secret Scanner** (TruffleHog)
   - Extension ID: `redhat.vscode-yaml`
   - Scans for secrets in real-time

### IntelliJ / PyCharm

1. **SonarLint** - Real-time quality and security
   - Settings → Plugins → Install SonarLint

2. **Built-in Security** - Enable in Settings
   - Settings → Editor → Inspections → Python → Security

### OWASP Top 10 Coverage

The pre-commit hooks and IDE extensions detect:
- **A01:2021 - Broken Access Control** (Semgrep)
- **A02:2021 - Cryptographic Failures** (Bandit, Gitleaks)
- **A03:2021 - Injection** (SQL, NoSQL, Command - Bandit/Semgrep)
- **A04:2021 - Insecure Design** (SonarLint, Semgrep)
- **A05:2021 - Security Misconfiguration** (Semgrep)
- **A06:2021 - Vulnerable Components** (pip-audit in CI)
- **A07:2021 - Auth Failures** (Bandit, Semgrep)
- **A08:2021 - Data Integrity** (Semgrep)
- **A09:2021 - Logging Errors** (Bandit)
- **A10:2021 - SSRF** (Semgrep)

## Docs

See `docs/` (French report, quality gates, manual GitHub secrets setup).
