# Demo Branches Documentation

This document describes the demo branches created to demonstrate security detection capabilities of the DevSecOps pipeline.

## Purpose of Demo Branches

These branches contain intentional security vulnerabilities to demonstrate that the pipeline's security controls work correctly. Each branch demonstrates a different type of security issue that should be detected by specific tools in the pipeline.

**Important**: These branches should never be merged into the main branch. They exist solely for demonstration and testing purposes.

## Demo Branches

### 1. demo/leaked-secret

**Purpose**: Demonstrate Gitleaks secrets detection

**What it contains**:
- File: `app/demo_secrets.py`
- Intentionally leaked fake AWS access key (example format: AKIA...)
- Intentionally leaked fake API key (example format: sk-...)

**Expected detection**:
- **Tool**: Gitleaks
- **Stage**: Secrets Scan
- **Result**: BLOCK - Pipeline should fail immediately
- **Error message**: "Gitleaks found secrets - blocking pipeline"

**How to test**:
```bash
git checkout demo/leaked-secret
# This should trigger Gitleaks detection in pre-commit hooks
# In Jenkins pipeline, this should fail at the Secrets Scan stage
```

**What to document**:
- Screenshot of Gitleaks detection in pre-commit hooks
- Screenshot of Jenkins pipeline failure at Secrets Scan stage
- Screenshot of Gitleaks report showing the leaked secrets

**Fix**:
```bash
git checkout master
# The fix is simply not having the secrets in the code
```

### 2. demo/vulnerable-dependency

**Purpose**: Demonstrate dependency vulnerability detection (SCA)

**What it contains**:
- Modified: `requirements.txt`
- Added: `requests==2.6.0` (old version with known vulnerabilities)
- Vulnerability: CVE-2023-32681 and others

**Expected detection**:
- **Tool**: Trivy (filesystem scan) and/or pip-audit
- **Stage**: Scan Dependencies
- **Result**: BLOCK - Pipeline should fail
- **Error message**: "Trivy found X CRITICAL and Y HIGH vulnerabilities - blocking pipeline"

**How to test**:
```bash
git checkout demo/vulnerable-dependency
# In Jenkins pipeline, this should fail at the Scan Dependencies stage
```

**What to document**:
- Screenshot of Trivy dependency scan report
- Screenshot of Jenkins pipeline failure at Scan Dependencies stage
- Screenshot showing the specific vulnerable dependency

**Fix**:
```bash
git checkout master
# The fix is using the current, secure version of requests
```

### 3. demo/insecure-code

**Purpose**: Demonstrate SAST (Static Application Security Testing) detection

**What it contains**:
- File: `app/demo_insecure.py`
- `eval()` with user input (code injection)
- `exec()` with user input (code injection)
- Hardcoded password
- Weak MD5 hash

**Expected detection**:
- **Tools**: Semgrep and Bandit
- **Stage**: SAST
- **Result**: BLOCK - Pipeline should fail
- **Error messages**: 
  - Semgrep: Multiple security rule violations
  - Bandit: Multiple high-severity issues

**How to test**:
```bash
git checkout demo/insecure-code
# This should trigger Semgrep/Bandit in pre-commit hooks
# In Jenkins pipeline, this should fail at the SAST stage
```

**What to document**:
- Screenshot of Semgrep findings
- Screenshot of Bandit findings
- Screenshot of Jenkins pipeline failure at SAST stage
- Screenshot showing specific insecure code patterns

**Fix**:
```bash
git checkout master
# The fix is removing the insecure code patterns
# In real scenarios, would replace with secure alternatives
```

### 4. demo/vulnerable-image

**Purpose**: Demonstrate container image vulnerability detection

**What it contains**:
- Modified: `Dockerfile`
- Changed base image from `python:3.11-slim` to `python:3.7-slim`
- Old Python 3.7 image has known vulnerabilities

**Expected detection**:
- **Tool**: Trivy (image scan)
- **Stage**: Docker Scan
- **Result**: BLOCK - Pipeline should fail
- **Error message**: "Trivy image scan found X CRITICAL and Y HIGH vulnerabilities - blocking pipeline"

**How to test**:
```bash
git checkout demo/vulnerable-image
# In Jenkins pipeline, this should fail at the Docker Scan stage
```

**What to document**:
- Screenshot of Trivy image scan report
- Screenshot of Jenkins pipeline failure at Docker Scan stage
- Screenshot showing vulnerable base image layers

**Fix**:
```bash
git checkout master
# The fix is using the current, secure base image
```

## Testing Procedure

### 1. Pre-commit Hook Testing

For each demo branch:

```bash
# Checkout the demo branch
git checkout demo/leaked-secret  # or other demo branch

# Try to commit (pre-commit hooks should fail)
git add .
git commit -m "Test commit"

# Expected: Pre-commit hooks should fail
# Document the specific tool that failed and the error message
```

### 2. Jenkins Pipeline Testing

For each demo branch:

```bash
# Push the demo branch to trigger Jenkins
git push origin demo/leaked-secret  # or other demo branch

# Monitor Jenkins pipeline execution
# Expected: Pipeline should fail at the expected stage
# Document the stage that failed and the error message
```

### 3. Clean Branch Testing

After testing all demo branches:

```bash
# Switch to clean master branch
git checkout master

# Push to verify green pipeline
git push origin master

# Expected: Pipeline should succeed end-to-end
# Document the successful run with all security gates passed
```

## Documentation Requirements

For each demo branch, capture:

### Failed Run Documentation
1. **Branch name**: demo/xxx
2. **Tool that detected the issue**: Gitleaks/Semgrep/Bandit/Trivy/etc.
3. **Pipeline stage that failed**: Secrets Scan/SAST/Scan Dependencies/Docker Scan
4. **Error message**: Exact error message from the pipeline
5. **Screenshot of pipeline failure**: Jenkins UI showing red failure
6. **Screenshot of tool report**: Specific scanner report showing findings
7. **Screenshot of code**: The vulnerable code that caused the failure

### Successful Run Documentation
1. **Branch**: master (clean)
2. **Pipeline result**: SUCCESS
3. **All stages passed**: Screenshot of green pipeline
4. **Deployment confirmation**: Screenshot of Docker Hub image
5. **Vercel deployment**: Screenshot of successful Vercel deployment
6. **Smoke test**: Screenshot of /health endpoint response

## Screenshot Organization

Organize screenshots in a structured way:

```
screenshots/
├── demo-branches/
│   ├── leaked-secret/
│   │   ├── pre-commit-failure.png
│   │   ├── jenkins-pipeline-failure.png
│   │   ├── gitleaks-report.png
│   │   └── vulnerable-code.png
│   ├── vulnerable-dependency/
│   │   ├── jenkins-pipeline-failure.png
│   │   ├── trivy-fs-report.png
│   │   └── requirements.txt.png
│   ├── insecure-code/
│   │   ├── pre-commit-failure.png
│   │   ├── jenkins-pipeline-failure.png
│   │   ├── semgrep-report.png
│   │   ├── bandit-report.png
│   │   └── insecure-code.png
│   └── vulnerable-image/
│       ├── jenkins-pipeline-failure.png
│       ├── trivy-image-report.png
│       └── dockerfile.png
└── clean-run/
    ├── green-pipeline.png
    ├── docker-hub-image.png
    ├── vercel-deployment.png
    └── health-check.png
```

## Analysis and Reporting

### Report Content

In the final report (docs/REPORT.md), include:

1. **Introduction**: Purpose of demo branches
2. **Methodology**: How each vulnerability was introduced
3. **Results**: Summary table of detection results

| Branch | Vulnerability Type | Tool Detected | Stage Failed | Result |
|-------|-------------------|---------------|--------------|--------|
| demo/leaked-secret | Leaked secret | Gitleaks | Secrets Scan | BLOCK |
| demo/vulnerable-dependency | Vulnerable dependency | Trivy | Scan Dependencies | BLOCK |
| demo/insecure-code | Insecure code patterns | Semgrep/Bandit | SAST | BLOCK |
| demo/vulnerable-image | Vulnerable base image | Trivy | Docker Scan | BLOCK |
| master | Clean | N/A | N/A | SUCCESS |

4. **Screenshots**: Embedded screenshots with explanations
5. **Analysis**: Effectiveness of each security control
6. **Conclusion**: Pipeline successfully detects all introduced vulnerabilities

## Cleanup After Testing

After completing demonstrations:

```bash
# Delete demo branches (optional, but recommended)
git branch -D demo/leaked-secret
git branch -D demo/vulnerable-dependency
git branch -D demo/insecure-code
git branch -D demo/vulnerable-image

# Or keep them for future demonstrations
# Just ensure they are never merged to master
```

## Important Notes

1. **Never merge demo branches**: These contain intentional vulnerabilities
2. **Use fake values only**: All secrets and keys are fake/dummy values
3. **Document everything**: Screenshots and error messages are crucial for the report
4. **Test clean branch**: Always verify master branch runs successfully
5. **Branch protection**: Consider setting up branch protection rules to prevent accidental merging

## Alternative Testing Methods

If Jenkins is not available for testing:

### Local Testing with Makefile

```bash
# Run all security scans locally
make scan-local

# This will run Gitleaks, Bandit, Semgrep, and Trivy locally
# Similar to what happens in the pipeline
```

### Manual Tool Testing

```bash
# Test Gitleaks
docker run --rm -v $(pwd):/src zricethezav/gitleaks:v8.18.0 detect --source /src

# Test Semgrep
docker run --rm -v $(pwd):/src returntocorp/semgrep:1.45.0 --config auto /src/app

# Test Bandit
docker run --rm -v $(pwd):/src python:3.11-slim bash -c "cd /src && pip install bandit && bandit -r app"

# Test Trivy
docker run --rm -v $(pwd):/src aquasec/trivy:0.47.0 fs /src
```

## Learning Outcomes

Through these demo branches, you should demonstrate:

1. **Shift-left security**: Pre-commit hooks catch issues early
2. **Pipeline security**: Jenkins blocks at appropriate stages
3. **Tool effectiveness**: Each tool detects its target vulnerabilities
4. **Quality gates**: Blocking thresholds work as designed
5. **Reporting**: Clear error messages and reports aid remediation
6. **Fix verification**: Clean branch runs successfully after fixes

## Contact

For questions about demo branches:
- Security Team: security@example.com
- DevOps Team: devops@example.com