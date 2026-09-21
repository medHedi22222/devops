# DevSecOps Flask App

A simple Flask application with JWT authentication protected by a comprehensive DevSecOps CI/CD pipeline.

## Getting Started

### Prerequisites
- Python 3.9+
- Docker
- Docker Compose

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. Create environment file:
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. Run the application:
```bash
python wsgi.py
```

### Running Tests

```bash
pytest --cov=app --cov-report=xml
```

### Environment Variables

- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `JWT_ACCESS_TOKEN_EXPIRES`: Token expiration time in seconds (default: 900)
- `DATABASE_URL`: Database connection string (default: sqlite:///app.db)

## API Endpoints

- `GET /health` - Health check
- `POST /auth/register` - User registration
- `POST /auth/login` - User login (returns JWT token)
- `GET /auth/me` - Get current user (requires JWT token)

## Pipeline

This project includes a comprehensive Jenkins CI/CD pipeline with integrated security controls:
- SAST (Semgrep, Bandit)
- SCA (Trivy, pip-audit)
- DAST (OWASP ZAP)
- Secrets scanning (Gitleaks)
- Container scanning (Trivy)
- SonarQube quality gates

See `docs/` for detailed documentation.
