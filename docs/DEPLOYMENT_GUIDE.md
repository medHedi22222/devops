# Deployment Guide

This document explains the deployment configuration for Docker Hub and Vercel, including the dual deployment strategy.

## Deployment Architecture

This project uses a **dual deployment strategy**:

1. **Docker Hub**: Container artifact deployment
   - Scanned and validated Docker image
   - Pushed to Docker Hub registry
   - Used for container-based deployments
   - Tagged with Git commit SHA and `latest`

2. **Vercel**: Serverless deployment
   - Serverless Python function deployment
   - Direct code deployment (not Docker-based)
   - Auto-scaling serverless infrastructure
   - Production URL for end users

**Important**: These are two separate delivery targets from the same validated commit. The Docker image is the scanned container artifact, while Vercel runs the code serverlessly.

## Docker Hub Deployment

### Image Tagging Strategy

Images are tagged as:
- `<dockerhub_user>/devsecops-flask:<git_sha_short>` - Immutable, specific to commit
- `<dockerhub_user>/devsecops-flask:latest` - Mutable, points to latest main branch commit

### Jenkins Pipeline Stage

```groovy
stage('Docker Push') {
    when {
        branch 'main'
    }
    steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', ...)]) {
            sh '''
                docker login -u $DOCKER_USER --password-stdin
                docker push ${DOCKER_IMAGE_NAME}:${DOCKER_TAG}
                docker push ${DOCKER_IMAGE_NAME}:latest
                docker logout
            '''
        }
    }
}
```

### Security Features

1. **Image scanning**: Trivy scans before push
2. **No secrets**: Secrets injected at runtime via environment variables
3. **Non-root user**: Container runs as non-root user
4. **Minimal base**: Uses slim Python image
5. **Health check**: Built-in health check endpoint
6. **Multi-stage**: Reduces final image size and attack surface

### Manual Docker Hub Setup

1. **Create Docker Hub account**: https://hub.docker.com/
2. **Create access token**:
   - Navigate to Account Settings → Security
   - Click "New Access Token"
   - Choose appropriate permissions (Read, Write, Delete)
   - Copy the token (you won't see it again)
3. **Create Jenkins credential**:
   - Jenkins → Credentials → System → Global credentials
   - Add "Username with password"
   - Username: Docker Hub username
   - Password: Access token
   - ID: `dockerhub-creds`

### Using the Docker Image

```bash
# Pull the image
docker pull yourusername/devsecops-flask:latest

# Run with environment variables
docker run -d -p 5000:5000 \
  --env-file .env \
  yourusername/devsecops-flask:latest

# Run specific commit
docker run -d -p 5000:5000 \
  --env-file .env \
  yourusername/devsecops-flask:abc1234
```

### Environment Variables for Docker

Required environment variables:
- `SECRET_KEY`: Flask secret key (≥32 characters)
- `JWT_SECRET_KEY`: JWT signing key (≥32 characters)
- `JWT_ACCESS_TOKEN_EXPIRES`: Token expiry in seconds (default: 900)
- `DATABASE_URL`: Database connection string (default: sqlite:///app.db)

## Vercel Deployment

### Vercel Configuration

The `vercel.json` file configures Vercel deployment:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "wsgi.py"
    }
  ]
}
```

### Serverless Adaptations

#### Database Handling
Vercel's filesystem is read-only/ephemeral, so SQLite uses `/tmp`:

```python
# In app/config.py
if os.environ.get('VERCEL') or DATABASE_URL.startswith('sqlite:///'):
    if not DATABASE_URL.startswith('sqlite:////tmp'):
        DATABASE_URL = DATABASE_URL.replace('sqlite:///', 'sqlite:////tmp/')
```

#### WSGI Entry Point
The `wsgi.py` file serves as the Vercel entry point:

```python
import os
from app import create_app

app = create_app()

if os.environ.get('VERCEL'):
    os.environ['DATABASE_URL'] = 'sqlite:////tmp/app.db'
```

### Jenkins Pipeline Stage

```groovy
stage('Deploy Vercel') {
    when {
        branch 'main'
    }
    steps {
        withCredentials([string(credentialsId: 'vercel-token', ...), ...]) {
            sh '''
                npm install -g vercel
                export VERCEL_ORG_ID=$VERCEL_ORG_ID
                export VERCEL_PROJECT_ID=$VERCEL_PROJECT_ID
                vercel deploy --prod --yes --token=$VERCEL_TOKEN
                
                # Smoke test
                DEPLOYMENT_URL=$(vercel ls --prod ...)
                curl -f $DEPLOYMENT_URL/health || exit 1
            '''
        }
    }
}
```

### Manual Vercel Setup

1. **Create Vercel account**: https://vercel.com/
2. **Create new project**:
   - Connect your Git repository
   - Configure build settings (if not using vercel.json)
   - Set environment variables
3. **Get project IDs**:
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Link project
   vercel link
   
   # Get IDs from .vercel/project.json
   cat .vercel/project.json
   ```
4. **Create access token**:
   - Vercel dashboard → Settings → Tokens
   - Create new token with appropriate scope
5. **Create Jenkins credentials**:
   - `vercel-token`: Vercel access token
   - `vercel-org-id`: Organization ID from project.json
   - `vercel-project-id`: Project ID from project.json

### Vercel Environment Variables

Set these in Vercel dashboard → Settings → Environment Variables:

- `SECRET_KEY`: Strong random string (≥32 characters)
- `JWT_SECRET_KEY`: Strong random string (≥32 characters)
- `JWT_ACCESS_TOKEN_EXPIRES`: 900 (15 minutes)
- `DATABASE_URL`: Optional (defaults to sqlite:////tmp/app.db)

**Note**: Use different values for Production, Preview, and Development environments.

### Vercel Limitations

1. **Ephemeral filesystem**: Database resets on each deployment
   - **Solution**: Use external database (PostgreSQL, MongoDB) for production
   - **Current demo**: Uses SQLite in /tmp for demonstration purposes

2. **Execution timeout**: Serverless functions have timeout limits
   - **Current config**: 10 seconds (configurable in vercel.json)
   - **Solution**: Optimize database queries, use background jobs

3. **Cold starts**: First request after inactivity may be slower
   - **Solution**: Use Vercel's Pro plan for reserved instances

### Testing Vercel Deployment

```bash
# Health check
curl https://your-app.vercel.app/health

# Test authentication
curl -X POST https://your-app.vercel.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password"}'
```

## Deployment Flow

### Complete Deployment Pipeline

1. **Code passes all security gates**:
   - Tests pass
   - No secrets found
   - SAST issues acceptable
   - Dependencies safe
   - Container safe
   - DAST findings acceptable

2. **Docker image built and scanned**:
   - Multi-stage build
   - Image scanned with Trivy
   - SBOM generated

3. **Staging deployment**:
   - Container runs in staging network
   - DAST scan performed
   - Runtime security validated

4. **Dual deployment** (only on main branch):
   - **Docker Hub**: Pushed scanned image
   - **Vercel**: Deployed serverless code

5. **Smoke tests**:
   - Docker Hub: Verify image availability
   - Vercel: Verify endpoint accessibility

## Rollback Procedures

### Docker Hub Rollback

```bash
# Pull previous version
docker pull yourusername/devsecops-flask:previous-commit-sha

# Deploy previous version
docker run -d -p 5000:5000 \
  --env-file .env \
  yourusername/devsecops-flask:previous-commit-sha
```

### Vercel Rollback

```bash
# View deployment history
vercel ls

# Rollback to specific deployment
vercel rollback <deployment-url>

# Or via Vercel dashboard:
# Navigate to project → Deployments → Click rollback
```

## Monitoring

### Docker Hub Monitoring

- **Image pulls**: View usage statistics in Docker Hub dashboard
- **Security scan results**: Check Trivy reports
- **Image size**: Monitor for unexpected growth

### Vercel Monitoring

- **Deployments**: View deployment history in Vercel dashboard
- **Analytics**: Built-in analytics for traffic and performance
- **Logs**: View function logs in Vercel dashboard
- **Error tracking**: Use Vercel's error tracking or integrate with Sentry

## Troubleshooting

### Docker Hub Issues

**Authentication failure**:
- Verify access token is valid
- Check Jenkins credential configuration
- Ensure token has appropriate permissions

**Image not found**:
- Verify image was pushed successfully
- Check Docker Hub repository name
- Verify image tag matches expected format

### Vercel Issues

**Deployment fails**:
- Check Vercel deployment logs
- Verify environment variables are set
- Ensure wsgi.py is correctly configured
- Check Python version compatibility

**Health check fails**:
- Verify app is running correctly
- Check database connectivity
- Review Vercel function logs
- Ensure /health endpoint is accessible

**Database issues**:
- Remember Vercel filesystem is ephemeral
- Consider using external database for production
- Check /tmp directory permissions

## Security Considerations

### Docker Hub Security

1. **Access tokens**: Use tokens instead of passwords
2. **Private repositories**: Consider private repos for sensitive apps
3. **Image scanning**: Always scan before pulling
4. **Base images**: Use official, scanned base images
5. **Secrets management**: Never bake secrets into images

### Vercel Security

1. **Environment variables**: Never commit secrets to code
2. **HTTPS only**: Vercel automatically enforces HTTPS
3. **Rate limiting**: Configure rate limiting in your app
4. **Input validation**: Validate all user inputs
5. **Dependencies**: Keep dependencies updated

## Cost Considerations

### Docker Hub Costs

- **Free tier**: Unlimited public repositories
- **Pro tier**: Private repositories, team features
- **Storage**: Based on image size and number of images

### Vercel Costs

- **Hobby**: Free for personal projects
- **Pro**: $20/month for production workloads
- **Enterprise**: Custom pricing for large teams

## Best Practices

1. **Tag images with commit SHA**: For reproducibility
2. **Use separate environments**: Development, staging, production
3. **Monitor deployments**: Track deployment success/failure rates
4. **Automate rollbacks**: Have automated rollback procedures
5. **Test locally first**: Test changes locally before deployment
6. **Keep dependencies updated**: Regular dependency updates
7. **Monitor costs**: Track usage and costs for both platforms
8. **Document deployments**: Keep deployment records and changelogs

## Comparison: Docker Hub vs Vercel

| Aspect | Docker Hub | Vercel |
|--------|------------|--------|
| **Deployment Type** | Container image | Serverless code |
| **Use Case** | Container orchestration | Web applications |
| **Scaling** | Manual/Kubernetes | Automatic |
| **Cold Starts** | None | Possible |
| **Filesystem** | Persistent | Ephemeral |
| **Database** | Any | External recommended |
| **Cost Model** | Storage/bandwidth | Usage-based |
| **Monitoring** | Basic | Built-in analytics |
| **Security** | Image scanning | Runtime security |

## Contact

For deployment issues:
- DevOps Team: devops@example.com
- Infrastructure Team: infra@example.com