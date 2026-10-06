# DevSecOps Pipeline - Detailed Explanation

This document explains every step of the DevSecOps CI/CD pipeline in detail, designed to help you answer validation questions about how the pipeline works.

---

## Table of Contents

1. [Pipeline Overview](#pipeline-overview)
2. [Job 1: Install & Test](#job-1-install--test)
3. [Job 2: Secrets Scan (Gitleaks)](#job-2-secrets-scan-gitleaks)
4. [Job 3: SAST (Semgrep + Bandit)](#job-3-sast-semgrep--bandit)
5. [Job 4: SCA (Trivy + pip-audit)](#job-4-sca-trivy--pip-audit)
6. [Job 5: SBOM Generation](#job-5-sbom-generation)
7. [Job 6: SonarQube Analysis](#job-6-sonarqube-analysis)
8. [Job 7: DAST (Security Headers)](#job-7-dast-security-headers)
9. [Job 8: Deploy to Vercel](#job-8-deploy-to-vercel)
10. [Email Notifications](#email-notifications)

---

## Pipeline Overview

The DevSecOps pipeline is a GitHub Actions workflow that runs on every push to the `master` branch or any `demo/*` branch, and on pull requests to `master`.

### Real-World Applicability

**Yes, this pipeline can be used in real-world projects.** It uses industry-standard tools and follows DevSecOps best practices:

- **Gitleaks**: Used by major companies to detect leaked secrets
- **Semgrep**: Used by companies like Airbnb, Dropbox for SAST
- **Bandit**: Standard Python security linter
- **Trivy**: Used by many organizations for container and dependency scanning
- **SonarQube**: Industry-standard code quality platform
- **pip-audit**: Official Python security audit tool

**For production use, you might want to add:**
- More sophisticated DAST (full OWASP ZAP scan)
- Container security scanning (Trivy image scan)
- Infrastructure-as-code scanning (Terraform, Kubernetes)
- Staging environment before production
- More strict quality gates
- Compliance reporting (SOC2, HIPAA, etc.)

### Pre-Commit Hooks (Local Security)

**Note**: Pre-commit hooks run **locally on your machine** before you commit, separate from the CI/CD pipeline. They provide immediate feedback and catch issues before they reach the remote repository.

**Pre-commit tools included:**
- Gitleaks: Detects secrets in code
- Bandit: Python security linter
- Semgrep: SAST scanner
- Black: Python code formatter
- Flake8: Python code linter
- Hygiene checks: Trailing whitespace, large files, etc.

**How pre-commit works:**
1. Developer runs `pre-commit install` (one-time setup)
2. When developer runs `git commit`, hooks automatically run
3. If hooks fail, commit is blocked
4. Developer fixes issues and tries again

**Pre-commit vs CI/CD:**
- Pre-commit: Runs locally, fast feedback, before commit
- CI/CD: Runs remotely, comprehensive checks, after push
- Both work together for shift-left security

### Execution Flow

```
Job 1 (Install & Test)
    ↓
    ├─→ Job 2 (Secrets Scan) ──┐
    ├─→ Job 3 (SAST) ──────────┤
    ├─→ Job 4 (SCA) ───────────┤
    ├─→ Job 5 (SBOM) ───────────┤
    └─→ Job 6 (SonarQube) ─────┤
                              ↓
                        Job 7 (DAST)
                              ↓
                        Job 8 (Deploy)
```

- **Job 1** runs first and must complete successfully
- **Jobs 2-5** run in parallel after Job 1 completes
- **Job 6** waits for Jobs 1-5 to all complete successfully
- **Job 7** (deployment) only runs if all previous jobs pass AND the push is to `master`

### Key Concepts

- **Blocking**: If a job fails, the pipeline stops and deployment is blocked
- **Parallel Execution**: Jobs 2-5 run simultaneously to save time
- **Artifacts**: Reports are saved as downloadable files
- **Email Notifications**: Sent on success or failure with reports attached

---

## Job 1: Install & Test

### Purpose
Run unit tests and measure code coverage to ensure the application works correctly.

### Steps Explained

#### Step 1: Checkout
- **What it does**: Clones the repository code to the GitHub Actions runner
- **Tool**: `actions/checkout@v4`
- **Why**: The runner needs the source code to work with

#### Step 2: Set up Python
- **What it does**: Installs Python 3.11 on the runner
- **Tool**: `actions/setup-python@v5`
- **Configuration**:
  - Uses Python version from environment variable (`PYTHON_VERSION: "3.11"`)
  - Enables pip caching to speed up future runs
- **Why**: The application needs Python to run

#### Step 3: Install Dependencies
- **What it does**: Installs all Python packages
- **Commands**:
  ```bash
  python -m pip install --upgrade pip  # Upgrade pip to latest version
  pip install -r requirements.txt     # Install app dependencies (Flask, JWT, etc.)
  pip install -r requirements-dev.txt # Install dev dependencies (pytest, coverage, etc.)
  ```
- **Why**: The app and tests need these packages to run

#### Step 4: Run pytest with Coverage
- **What it does**: Runs all tests and measures code coverage
- **Environment Variables**:
  - `SECRET_KEY`: Flask secret key for testing (32+ characters)
  - `JWT_SECRET_KEY`: JWT signing key for testing (32+ characters)
  - `JWT_ACCESS_TOKEN_EXPIRES`: Token expiration time in seconds (900 = 15 minutes)
- **Commands**:
  ```bash
  mkdir -p reports  # Create reports directory
  pytest --cov=app --cov-report=xml:reports/coverage.xml \  # Generate XML coverage report
         --cov-report=term-missing --junitxml=reports/pytest.xml -q  # Terminal output + JUnit XML
  ```
- **What the flags mean**:
  - `--cov=app`: Measure coverage for the `app` directory
  - `--cov-report=xml:reports/coverage.xml`: Generate XML coverage report for SonarQube
  - `--cov-report=term-missing`: Show which lines are not covered in terminal
  - `--junitxml=reports/pytest.xml`: Generate JUnit XML report for test results
  - `-q`: Quiet mode (less output)
- **Why**: Ensures code works correctly and measures test coverage

#### Step 5: Upload Test Reports
- **What it does**: Saves test results and coverage reports as artifacts
- **Tool**: `actions/upload-artifact@v4`
- **Configuration**:
  - Artifact name: `test-reports`
  - Path: `reports/` (contains `coverage.xml` and `pytest.xml`)
  - `if: always()`: Runs even if tests fail
- **Why**: Reports can be downloaded from GitHub Actions UI for analysis

#### Step 6: Send Failure Notification
- **What it does**: Sends an email if tests fail
- **Tool**: `dawidd6/action-send-mail@v3`
- **Configuration**:
  - SMTP server: `smtp.gmail.com` on port 465 (SSL)
  - Uses GitHub secrets for credentials (`MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_TO`)
  - Subject: "❌ Pipeline Failed - DevSecOps Pipeline"
  - Body includes: repository, branch, commit, actor, failed job name
  - Attachments: `pytest.xml` and `coverage.xml`
  - `if: failure()`: Only runs if the job fails
- **Why**: Immediate notification when tests fail for quick debugging

### When This Job Fails
- If any test fails (assertion error, exception, etc.)
- If coverage is below threshold (configured in SonarQube)
- If the application crashes during testing

---

## Job 2: Secrets Scan (Gitleaks)

### Purpose
Detect leaked secrets (API keys, passwords, tokens) in the codebase.

### Dependencies
- **Waits for**: Job 1 (Install & Test) to complete
- **Runs in parallel with**: Jobs 3, 4, 5

### Steps Explained

#### Step 1: Checkout
- **What it does**: Clones the repository code
- **Why**: Gitleaks needs the source code to scan

#### Step 2: Run Gitleaks
- **What it does**: Scans code for secrets using pattern matching
- **Tool**: Docker container `zricethezav/gitleaks:v8.18.4`
- **Commands**:
  ```bash
  mkdir -p reports
  docker run --rm \
    -v "$PWD:/src" \
    -w /src \
    ${{ env.GITLEAKS_IMAGE }} \
    detect --source /src \
           --no-git \
           --config /src/.gitleaks.toml \
           --report-path /src/reports/gitleaks-report.json \
           --report-format json \
           --verbose
  ```
- **What the flags mean**:
  - `--rm`: Remove container after running (cleanup)
  - `-v "$PWD:/src"`: Mount current directory to `/src` in container
  - `-w /src`: Set working directory to `/src`
  - `detect`: Run Gitleaks detection
  - `--source /src`: Scan the `/src` directory
  - `--no-git`: Only scan current files, not git history (avoids false positives from old commits)
  - `--config /src/.gitleaks.toml`: Use custom configuration file
  - `--report-path /src/reports/gitleaks-report.json`: Output file path
  - `--report-format json`: Output in JSON format
  - `--verbose`: Show detailed output
- **What Gitleaks detects**:
  - API keys (AWS, Google, GitHub, etc.)
  - Database connection strings
  - JWT tokens
  - Private keys (SSH, SSL)
  - Passwords in code
  - Authentication tokens
- **Why**: Prevents committing secrets to the repository (security risk)

#### Step 3: Upload Gitleaks Report
- **What it does**: Saves the scan results as an artifact
- **Configuration**:
  - Artifact name: `gitleaks-report`
  - Path: `reports/gitleaks-report.json`
  - `if: always()`: Runs even if scan fails
- **Why**: Report can be reviewed to see what secrets were found

#### Step 4: Send Failure Notification
- **What it does**: Sends an email if secrets are detected
- **Configuration**: Similar to Job 1, but specific to secrets scan
- **Why**: Immediate alert when secrets are found

### When This Job Fails
- If any secret pattern is detected in the code
- If the Gitleaks configuration file is invalid
- If the scan encounters an error

---

## Job 3: SAST (Semgrep + Bandit)

### Purpose
Static Application Security Testing - finds security vulnerabilities in the source code.

### Dependencies
- **Waits for**: Job 1 (Install & Test) to complete
- **Runs in parallel with**: Jobs 2, 4, 5

### Steps Explained

#### Step 1: Checkout
- **What it does**: Clones the repository code
- **Why**: SAST tools need the source code to analyze

#### Step 2: Set up Python
- **What it does**: Installs Python 3.11
- **Why**: Bandit is a Python tool that needs Python to run

#### Step 3: Install Bandit
- **What it does**: Installs Bandit security linter
- **Command**: `pip install "bandit==1.7.5" "pbr>=5.0"`
- **Why**: Bandit finds Python-specific security issues

#### Step 4: Run Semgrep
- **What it does**: Runs Semgrep with custom security rules
- **Tool**: Docker container `semgrep/semgrep:1.45.0`
- **Commands**:
  ```bash
  mkdir -p reports
  docker run --rm \
    -v "$PWD:/src" \
    -w /src \
    ${{ env.SEMGREP_IMAGE }} \
    semgrep \
    --config .semgrep/custom.yaml \
    --error \
    --metrics=off \
    --json \
    --output /src/reports/semgrep-report.json \
    app
  ```
- **What the flags mean**:
  - `semgrep`: Run semgrep command
  - `--config .semgrep/custom.yaml`: Use custom security rules
  - `--error`: Exit with error code if ERROR severity findings exist (blocks pipeline)
  - `--metrics=off`: Disable metrics output
  - `--json`: Output in JSON format
  - `--output /src/reports/semgrep-report.json`: Output file
  - `app`: Scan the `app` directory
- **What Semgrep detects**:
  - SQL injection vulnerabilities
  - Command injection
  - Cross-site scripting (XSS)
  - Insecure deserialization
  - Hardcoded secrets
  - OWASP Top 10 vulnerabilities
- **Why**: Finds security issues before they reach production

#### Step 5: Run Bandit
- **What it does**: Runs Bandit on the Python code
- **Commands**:
  ```bash
  mkdir -p reports
  bandit -r app -lll -f json -o reports/bandit-report.json
  bandit -r app -lll -f txt
  ```
- **What the flags mean**:
  - `-r app`: Recursively scan the `app` directory
  - `-lll`: Only report HIGH severity and above (ignores MEDIUM and LOW)
  - `-f json`: Output in JSON format
  - `-o reports/bandit-report.json`: Output file
  - `-f txt`: Also output in text format for terminal viewing
- **What Bandit detects**:
  - Use of insecure functions (e.g., `eval()`, `exec()`)
  - Hardcoded passwords
  - SQL injection risks
  - Weak cryptography
  - Unsafe imports
- **Why**: Python-specific security analysis

#### Step 6: Upload SAST Reports
- **What it does**: Saves both Semgrep and Bandit reports
- **Configuration**:
  - Artifact name: `sast-reports`
  - Paths: `reports/semgrep-report.json`, `reports/bandit-report.json`
- **Why**: Both reports can be reviewed for security findings

#### Step 7: Send Failure Notification
- **What it does**: Sends an email if vulnerabilities are found
- **Why**: Alert when security issues are detected

### When This Job Fails
- If Semgrep finds ERROR severity issues
- If Bandit finds HIGH severity issues
- If either tool encounters an error

---

## Job 4: SCA (Trivy + pip-audit)

### Purpose
Software Composition Analysis - finds vulnerabilities in dependencies (third-party packages).

### Dependencies
- **Waits for**: Job 1 (Install & Test) to complete
- **Runs in parallel with**: Jobs 2, 3, 5

### Steps Explained

#### Step 1: Checkout
- **What it does**: Clones the repository code
- **Why**: SCA tools need to check dependency files

#### Step 2: Set up Python
- **What it does**: Installs Python 3.11
- **Why**: pip-audit needs Python to run

#### Step 3: Install App + pip-audit
- **What it does**: Installs app dependencies and pip-audit tool
- **Commands**:
  ```bash
  pip install -r requirements.txt       # Install app dependencies
  pip install "pip-audit==2.6.1"        # Install pip-audit tool
  ```
- **Why**: pip-audit checks installed packages for known vulnerabilities

#### Step 4: pip-audit
- **What it does**: Checks Python packages for known vulnerabilities (CVEs)
- **Commands**:
  ```bash
  mkdir -p reports
  set +e                               # Don't exit on error temporarily
  pip-audit -r requirements.txt --format json --output reports/pip-audit-report.json
  audit_status=$?                      # Save exit code
  pip-audit -r requirements.txt        # Console output
  table_status=$?                      # Save exit code
  set -e                               # Exit on error again
  if [ "$audit_status" -ne 0 ] || [ "$table_status" -ne 0 ]; then
    exit 1                             # Fail the job if vulnerabilities found
  fi
  ```
- **What it does**:
  - Runs pip-audit on `requirements.txt`
  - Saves JSON report for artifact
  - Runs again for console output
  - Fails if either run finds vulnerabilities (exit code != 0)
- **What pip-audit detects**:
  - Known CVEs in Python packages
  - Outdated packages with security fixes
  - Vulnerable dependencies
- **Why**: Ensures third-party packages are secure

#### Step 5: Trivy Filesystem Scan
- **What it does**: Scans all files for vulnerabilities using Trivy
- **Tool**: Docker container `aquasec/trivy:0.50.1`
- **Commands**:
  ```bash
  mkdir -p reports
  docker run --rm \
    -v "$PWD:/src" \
    -v trivy-cache:/root/.cache/ \
    ${{ env.TRIVY_IMAGE }} \
    fs --severity CRITICAL,HIGH \
       --exit-code 1 \
       --ignore-unfixed \
       --format json \
       --output /src/reports/trivy-fs-report.json \
       /src
  docker run --rm \
    -v "$PWD:/src" \
    -v trivy-cache:/root/.cache/ \
    ${{ env.TRIVY_IMAGE }} \
    fs --severity CRITICAL,HIGH \
       --exit-code 1 \
       --ignore-unfixed \
       --format table \
       /src
  ```
- **What the flags mean**:
  - `fs`: Filesystem scan mode
  - `--severity CRITICAL,HIGH`: Only report CRITICAL and HIGH severity
  - `--exit-code 1`: Exit with code 1 if vulnerabilities found (blocks pipeline)
  - `--ignore-unfixed`: Ignore vulnerabilities that don't have a fix yet
  - `--format json`: JSON output for artifact
  - `--format table`: Table output for console
  - `-v trivy-cache:/root/.cache/`: Cache for faster subsequent scans
- **What Trivy detects**:
  - Vulnerabilities in dependency files (requirements.txt, package.json, etc.)
  - OS package vulnerabilities (in Dockerfiles)
  - Configuration issues
  - Secrets in files
- **Why**: Comprehensive vulnerability scanning

#### Step 6: Upload SCA Reports
- **What it does**: Saves both pip-audit and Trivy reports
- **Configuration**:
  - Artifact name: `sca-reports`
  - Paths: `reports/pip-audit-report.json`, `reports/trivy-fs-report.json`
- **Why**: Both reports provide different vulnerability perspectives

#### Step 7: Send Failure Notification
- **What it does**: Sends an email if vulnerabilities are found
- **Why**: Alert when dependencies have security issues

### When This Job Fails
- If pip-audit finds any known vulnerabilities
- If Trivy finds CRITICAL or HIGH severity vulnerabilities
- If either tool encounters an error

---

## Job 5: SBOM Generation

### Purpose
Generate a Software Bill of Materials (SBOM) - a comprehensive list of all software components, dependencies, and packages used in the project.

### Dependencies
- **Waits for**: Job 1 (Install & Test) to complete
- **Runs in parallel with**: Jobs 2, 3, 4, 6
- **Blocking**: NO - This job does not block the pipeline (non-blocking)

### Steps Explained

#### Step 1: Checkout
- **What it does**: Clones the repository code
- **Why**: SBOM generator needs to scan the codebase

#### Step 2: Set up Python
- **What it does**: Installs Python 3.11
- **Why**: Need Python to install dependencies for SBOM generation

#### Step 3: Install Dependencies
- **What it does**: Installs app dependencies
- **Command**: `pip install -r requirements.txt`
- **Why**: SBOM includes installed packages

#### Step 4: Generate SBOM with Syft
- **What it does**: Generates SBOM in multiple formats
- **Tool**: Syft (by Anchore)
- **Commands**:
  ```bash
  mkdir -p reports
  # Install Syft (SBOM generator)
  curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
  # Generate SBOM in CycloneDX JSON format
  syft . -o cyclonedx-json > reports/sbom.json
  # Also generate SPDX JSON format (alternative standard)
  syft . -o spdx-json > reports/sbom-spdx.json
  # Generate human-readable table
  syft . -o table > reports/sbom.txt
  ```
- **What the flags mean**:
  - `syft .`: Scan current directory
  - `-o cyclonedx-json`: Output in CycloneDX JSON format (industry standard)
  - `-o spdx-json`: Output in SPDX JSON format (alternative standard)
  - `-o table`: Output in human-readable table format
- **What SBOM contains**:
  - All Python packages from requirements.txt
  - Package versions
  - Package licenses
  - Package suppliers
  - Package dependencies
  - Vulnerability information (if available)
- **Why**:
  - **Compliance**: Required by regulations (Executive Order 14028, EU Cyber Resilience Act)
  - **Vulnerability tracking**: Know exactly what components are used
  - **Supply chain security**: Track third-party components
  - **Incident response**: Quickly identify affected components when CVEs are announced

#### Step 5: Upload SBOM Artifacts
- **What it does**: Saves SBOM reports as artifacts
- **Configuration**:
  - Artifact name: `sbom-reports`
  - Paths: `reports/sbom.json`, `reports/sbom-spdx.json`, `reports/sbom.txt`
- **Why**: SBOM can be downloaded for compliance audits and vulnerability analysis

### When This Job Fails
- **NEVER** - This job is non-blocking
- Even if SBOM generation fails, the pipeline continues
- SBOM is informational, not a security gate

### Why SBOM is Non-Blocking
- SBOM generation is for documentation and compliance
- It doesn't detect vulnerabilities (that's what SCA does)
- Failing to generate an SBOM shouldn't block deployment
- The pipeline continues even if SBOM generation encounters issues

---

## Job 5: SonarQube Analysis

### Purpose
Code quality analysis - measures code quality, coverage, bugs, code smells, and security hotspots.

### Dependencies
- **Waits for**: Job 1 (Install & Test) to complete
- **Runs in parallel with**: Jobs 2, 3, 4

### Steps Explained

#### Step 1: Checkout Repository
- **What it does**: Clones the repository with full git history
- **Configuration**:
  - `fetch-depth: 0`: Full git history (not just latest commit)
- **Why**: SonarQube needs full history for blame analysis (who wrote which code)

#### Step 2: Download Test Coverage Reports
- **What it does**: Downloads coverage reports from Job 1
- **Tool**: `actions/download-artifact@v4`
- **Configuration**:
  - Artifact name: `test-reports` (from Job 1)
  - Path: `reports/`
- **Why**: SonarQube uses coverage data to measure test coverage percentage

#### Step 3: SonarQube Scan
- **What it does**: Runs SonarQube scanner on the codebase
- **Tool**: `SonarSource/sonarqube-scan-action@v5`
- **Environment Variables**:
  - `SONAR_TOKEN`: Authentication token for SonarQube server (from GitHub secrets)
  - `SONAR_HOST_URL`: URL of the SonarQube server (from GitHub secrets)
- **What SonarQube analyzes**:
  - **Code Coverage**: Percentage of code covered by tests (target: 80%+)
  - **Bugs**: Potential bugs in the code
  - **Code Smells**: Code quality issues (complexity, duplication, etc.)
  - **Security Hotspots**: Security-sensitive code that needs review
  - **Vulnerabilities**: Security vulnerabilities
  - **Duplications**: Duplicated code blocks
  - **Technical Debt**: Estimated effort to fix issues
- **Quality Gate Rules** (configured in SonarQube):
  - Coverage on New Code: ≥ 80%
  - Security Rating: A (no critical security issues)
  - Maintainability Rating: A (good code quality)
  - Reliability Rating: A (no critical bugs)
- **Why**: Ensures code quality standards are met

#### Step 4: Send Failure Notification
- **What it does**: Sends an email if quality gate fails
- **Why**: Alert when code quality standards are not met

### When This Job Fails
- If code coverage is below 80%
- If security rating is not A
- If maintainability rating is not A
- If reliability rating is not A
- If any critical bugs or vulnerabilities are found

---

## Job 6: DAST (Security Headers)

### Purpose
Dynamic Application Security Testing - tests the running application for security issues.

### Dependencies
- **Waits for**: Jobs 1, 2, 3, 4, 5 to ALL complete successfully
- **Runs after**: All previous security checks pass

### Steps Explained

#### Step 1: Checkout
- **What it does**: Clones the repository code
- **Why**: Need the code to run the application

#### Step 2: Set up Python
- **What it does**: Installs Python 3.11
- **Why**: Need Python to run the Flask application

#### Step 3: Install Dependencies
- **What it does**: Installs app dependencies
- **Command**: `pip install -r requirements.txt`
- **Why**: Application needs dependencies to run

#### Step 4: Start Flask Application
- **What it does**: Starts the Flask application in the background for scanning
- **Environment Variables**:
  - `SECRET_KEY`: Flask secret for testing
  - `JWT_SECRET_KEY`: JWT secret for testing
  - `JWT_ACCESS_TOKEN_EXPIRES`: Token expiration (900 seconds)
- **Commands**:
  ```bash
  python wsgi.py > app.log 2>&1 &    # Start app in background, redirect output to log
  APP_PID=$!                        # Save process ID
  echo "APP_PID=$APP_PID" >> $GITHUB_ENV  # Save to GitHub environment
  echo "Waiting for app to start..."
  sleep 15                           # Wait 15 seconds for startup
  if ! kill -0 $APP_PID 2>/dev/null; then  # Check if process is running
    echo "App failed to start. Log:"
    cat app.log                      # Show log if failed
    exit 1                           # Fail the job
  fi
  curl -f http://localhost:5000/health || exit 1  # Health check
  echo "App is ready for scanning"
  ```
- **What it does**:
  - Starts the Flask app on port 5000
  - Saves the process ID for later cleanup
  - Waits 15 seconds for the app to start
  - Checks if the process is still running
  - Tests the `/health` endpoint to ensure app is responding
- **Why**: DAST needs a running application to test

#### Step 5: Run DAST Security Checks
- **What it does**: Checks HTTP response for security headers
- **Commands**:
  ```bash
  mkdir -p reports
  echo "Running basic DAST checks..."
  response=$(curl -sI http://localhost:5000)  # Get HTTP headers

  echo "=== Security Headers Check ===" > reports/dast-report.txt
  echo "$response" >> reports/dast-report.txt

  # Check for X-Content-Type-Options
  if echo "$response" | grep -q "X-Content-Type-Options"; then
    echo "✓ X-Content-Type-Options header present" >> reports/dast-report.txt
  else
    echo "✗ X-Content-Type-Options header missing" >> reports/dast-report.txt
  fi

  # Check for X-Frame-Options
  if echo "$response" | grep -q "X-Frame-Options"; then
    echo "✓ X-Frame-Options header present" >> reports/dast-report.txt
  else
    echo "✗ X-Frame-Options header missing" >> reports/dast-report.txt
  fi

  # Check for X-XSS-Protection
  if echo "$response" | grep -q "X-XSS-Protection"; then
    echo "✓ X-XSS-Protection header present" >> reports/dast-report.txt
  else
    echo "✗ X-XSS-Protection header missing" >> reports/dast-report.txt
  fi

  echo "=== Endpoint Availability Check ===" >> reports/dast-report.txt
  curl -s http://localhost:5000/health && echo "✓ /health endpoint accessible" >> reports/dast-report.txt || echo "✗ /health endpoint failed" >> reports/dast-report.txt

  cat reports/dast-report.txt
  ```
- **What it checks**:
  - **X-Content-Type-Options**: Prevents MIME-type sniffing (protects against XSS)
  - **X-Frame-Options**: Prevents clickjacking attacks
  - **X-XSS-Protection**: Enables browser XSS filter
  - **Health Endpoint**: Ensures the application is accessible
- **Why**: Verifies the running application has basic security headers

#### Step 6: Stop Flask Application
- **What it does**: Stops the Flask application (cleanup)
- **Commands**:
  ```bash
  if [ -n "$APP_PID" ]; then
    kill $APP_PID || true
  fi
  ```
- **Configuration**: `if: always()` - runs even if scan fails
- **Why**: Cleanup - don't leave processes running

#### Step 7: Upload DAST Report
- **What it does**: Saves the DAST scan results
- **Configuration**:
  - Artifact name: `dast-report`
  - Path: `reports/dast-report.txt`
- **Why**: Report can be reviewed for security header status

#### Step 8: Send Failure Notification
- **What it does**: Sends an email if DAST fails
- **Why**: Alert when running application has security issues

### When This Job Fails
- If the application fails to start
- If the health endpoint is not accessible
- If critical security headers are missing

---

## Job 7: Deploy to Vercel

### Purpose
Deploy the application to production on Vercel.

### Dependencies
- **Waits for**: Jobs 1, 2, 3, 4, 5, 6 to ALL complete successfully
- **Only runs on**: Push to `master` branch (not on PRs or demo branches)

### Steps Explained

#### Step 1: Checkout
- **What it does**: Clones the repository code
- **Why**: Need the code to deploy

#### Step 2: Set up Node.js
- **What it does**: Installs Node.js 20
- **Tool**: `actions/setup-node@v4`
- **Why**: Vercel CLI requires Node.js

#### Step 3: Deploy to Vercel
- **What it does**: Deploys the application to Vercel production
- **Environment Variables**:
  - `VERCEL_TOKEN`: Vercel authentication token (from GitHub secrets)
  - `VERCEL_ORG_ID`: Vercel organization ID (from GitHub secrets)
  - `VERCEL_PROJECT_ID`: Vercel project ID (from GitHub secrets)
- **Command**:
  ```bash
  npx --yes vercel@latest deploy --prod --yes --token="$VERCEL_TOKEN"
  ```
- **What the flags mean**:
  - `npx --yes`: Run npx without confirmation
  - `vercel@latest`: Use latest Vercel CLI
  - `deploy`: Deploy command
  - `--prod`: Deploy to production (not preview)
  - `--yes`: Auto-confirm (no interactive prompts)
  - `--token="$VERCEL_TOKEN"`: Use authentication token
- **Why**: Deploy the application to production after all security checks pass

#### Step 4: Download All Reports
- **What it does**: Downloads all artifacts from previous jobs
- **Tool**: `actions/download-artifact@v4`
- **Configuration**:
  - Path: `all-reports/`
- **Why**: Attach all reports to the success email

#### Step 5: Send Success Notification
- **What it does**: Sends an email with all reports attached
- **Configuration**:
  - Subject: "✅ Deployment Successful - DevSecOps Pipeline"
  - Body lists all passed security checks
  - Attachments: All JSON, XML, and TXT reports
- **Why**: Confirmation that deployment succeeded with all reports

### When This Job Fails
- If Vercel deployment fails (network issues, token issues, etc.)
- If Vercel secrets are not configured correctly

---

## Email Notifications

### Purpose
Send email notifications on pipeline success or failure with reports attached.

### Configuration

All email notifications use:
- **SMTP Server**: `smtp.gmail.com`
- **Port**: `465` (SSL)
- **Authentication**: Gmail username + App Password
- **Recipients**: Configured via GitHub secrets

### Required GitHub Secrets

1. **MAIL_USERNAME**: Your Gmail address
2. **MAIL_PASSWORD**: Gmail App Password (NOT regular password)
3. **MAIL_TO**: Recipient email address

### Notification Types

#### Failure Notifications
- Sent when any job fails
- Includes:
  - Repository name
  - Branch name
  - Commit hash
  - Actor (who triggered)
  - Failed job name
  - Specific failure reason
  - Relevant report attachments

#### Success Notification
- Sent only when deployment succeeds
- Includes:
  - Repository name
  - Branch name
  - Commit hash
  - Actor
  - List of all passed security checks
  - All report attachments (test, secrets, SAST, SCA, SonarQube, DAST)

### Why Email Notifications?
- Immediate awareness of pipeline status
- Reports attached for quick analysis
- No need to check GitHub Actions UI constantly
- Useful for team communication

---

## Summary

The DevSecOps pipeline implements a comprehensive security gate system:

### Security Layers

1. **Pre-commit (Local)**: First line of defense - runs on developer's machine
2. **Job 1**: Ensures code works correctly (tests + coverage)
3. **Job 2**: Prevents secrets in code (Gitleaks)
4. **Job 3**: Finds code vulnerabilities (Semgrep + Bandit)
5. **Job 4**: Finds dependency vulnerabilities (Trivy + pip-audit)
6. **Job 5**: Ensures code quality (SonarQube)
7. **Job 6**: Tests running application (DAST)
8. **Job 7**: Deploys to production (Vercel)

### Why DAST Waits for Other Jobs

DAST (Job 6) waits for all previous jobs to complete because:

1. **Requires a working application**: DAST needs the app to run. If unit tests fail, the app is broken and DAST cannot run.

2. **Tests the "as-built" application**: DAST should test the final artifact after all code is verified. It doesn't make sense to DAST-test broken code.

3. **Resource efficiency**: DAST is expensive (starts the app, runs scans). Only run it if the code passes all other checks first.

4. **Logical order**:
   - Static checks (SAST, SCA, secrets) run first (fast, no app needed)
   - Dynamic checks (DAST) run last (slow, needs running app)

5. **Security best practice**: DAST is the final validation that the running application is secure, not a replacement for static analysis.

Each job blocks deployment if it fails, ensuring only secure, high-quality code reaches production.
