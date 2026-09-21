# Manual Steps Documentation

This document lists all steps that must be performed manually outside of the repository.

## Prerequisites

1. Install Docker Desktop on your development machine
2. Install Docker Compose (usually included with Docker Desktop)
3. Ensure Docker is running before attempting to build images or start services

## Docker Installation and Testing

The Dockerfile and docker-compose.yml have been created, but Docker must be installed locally to test them:

```bash
# Build the Docker image
docker build -t devsecops-flask:test .

# Run the container with environment variables
docker run --env-file .env -p 5000:5000 devsecops-flask:test

# Start Jenkins and SonarQube infrastructure
cd infra
docker-compose up -d
```

## Steps that require manual intervention (from original requirements)

1. Create a **Docker Hub access token** (Account Settings → Security) → Jenkins credential `dockerhub-creds` (username + token).
2. Create a **Vercel project + token**, get `VERCEL_ORG_ID` and `VERCEL_PROJECT_ID` (`vercel link`) → Jenkins credentials.
3. Start Jenkins/SonarQube with `docker compose up -d`, install suggested plugins + SonarQube Scanner, HTML Publisher, Docker Pipeline, Credentials Binding, Mailer/Slack.
4. Create the SonarQube token → Jenkins credential `sonar-token`; configure the SonarQube server in Jenkins; create the webhook Sonar → Jenkins for `waitForQualityGate`.
5. Create the Jenkins multibranch pipeline pointing at the Git repo.
6. Set Vercel environment variables:
   - Navigate to Vercel project dashboard → Settings → Environment Variables
   - Add required variables:
     - `SECRET_KEY`: Strong random string (≥32 characters)
     - `JWT_SECRET_KEY`: Strong random string (≥32 characters)
     - `JWT_ACCESS_TOKEN_EXPIRES`: 900 (15 minutes)
     - `DATABASE_URL`: (optional, will default to sqlite:////tmp/app.db)
   - Select appropriate environments (Production, Preview, Development)
7. Configure Jenkins email notifications:
   - Configure SMTP server in Jenkins → Configure System → E-mail Notification
   - Set `$DEFAULT_RECIPIENTS` environment variable or configure in pipeline
   - Test email configuration
8. Take the screenshots for the report.
