# Test Failure Scenarios - How to Make Each Pipeline Stage Fail

This document explains exactly what changes to make in the application to cause each specific pipeline stage to fail. This is useful for demonstrating that the pipeline correctly detects and blocks security issues.

**Note**: Pre-commit hooks run **locally on your machine** before you commit. They are separate from the CI/CD pipeline but use similar tools (Gitleaks, Bandit, Semgrep).

---

## Table of Contents

1. [Pre-Commit Hook Failures](#pre-commit-hook-failures)
2. [Job 1: Install & Test Failures](#job-1-install--test-failures)
3. [Job 2: Secrets Scan Failures](#job-2-secrets-scan-failures)
4. [Job 3: SAST Failures](#job-3-sast-failures)
5. [Job 4: SCA Failures](#job-4-sca-failures)
6. [Job 5: SonarQube Failures](#job-5-sonarqube-failures)
7. [Job 6: DAST Failures](#job-6-dast-failures)

---

## Pre-Commit Hook Failures

### Scenario 1: Secret Detection (Gitleaks)

**What to change**: Add a secret to the code

**File**: Any file in the repository

**Change**:
```python
# Add this to any Python file:
API_KEY = "sk-1234567890abcdef1234567890abcdef"  # ← ADD THIS
```

**Result**:
- Pre-commit hook fails when you try to commit
- Commit is blocked
- Gitleaks shows the detected secret

**How to test**:
```bash
git add .
git commit -m "test"  # ← Will fail here
```

**Why it fails**: Gitleaks pre-commit hook detects secret patterns

---

### Scenario 2: Code Formatting (Black)

**What to change**: Add poorly formatted code

**File**: `app/auth.py`

**Change**:
```python
# Add this function with bad formatting:
def bad_format(x,y,z):return x+y+z  # ← NO SPACES, BAD FORMATTING
```

**Result**:
- Pre-commit hook fails
- Black reformats the code automatically
- You need to stage the changes and commit again

**How to test**:
```bash
git add .
git commit -m "test"  # ← Will fail, Black will fix it
git add .
git commit -m "test"  # ← Will succeed now
```

**Why it fails**: Black enforces PEP 8 formatting standards

---

### Scenario 3: Code Linting (Flake8)

**What to change**: Add code with linting errors

**File**: `app/auth.py`

**Change**:
```python
# Add this function with unused variable:
def lint_error():
    unused_var = 123  # ← UNUSED VARIABLE
    return True
```

**Result**:
- Pre-commit hook fails
- Flake8 shows the linting error (F841 unused variable)

**How to test**:
```bash
git add .
git commit -m "test"  # ← Will fail
```

**Why it fails**: Flake8 detects code style issues and unused variables

---

### Scenario 4: Security Linting (Bandit)

**What to change**: Add insecure code

**File**: `app/auth.py`

**Change**:
```python
# Add this function:
def insecure():
    exec("print('hello')")  # ← INSECURE
```

**Result**:
- Pre-commit hook fails
- Bandit detects use of exec()

**How to test**:
```bash
git add .
git commit -m "test"  # ← Will fail
```

**Why it fails**: Bandit pre-commit hook detects security issues

---

### Scenario 5: Trailing Whitespace

**What to change**: Add trailing whitespace

**File**: Any file

**Change**:
```python
# Add a line with trailing spaces:
print("hello")     # ← TRAILING SPACES
```

**Result**:
- Pre-commit hook fails
- Trailing whitespace is removed automatically

**How to test**:
```bash
git add .
git commit -m "test"  # ← Will fail, whitespace removed
git add .
git commit -m "test"  # ← Will succeed
```

**Why it fails**: Pre-commit hygiene hook detects and removes trailing whitespace

---

### How to Skip Pre-Commit Hooks (Not Recommended)

If you need to bypass pre-commit hooks (not recommended for security reasons):

```bash
git commit --no-verify -m "message"
```

**Warning**: This skips all security checks locally. The CI/CD pipeline will still run the same checks, so issues will still be caught.

---

## Job 1: Install & Test Failures

### Scenario 1: Test Failure

**What to change**: Make a test assertion fail

**File**: `tests/test_auth.py`

**Change**:
```python
# Find this test (around line 20-30):
def test_register_success(client):
    response = client.post('/auth/register', json={
        'username': 'testuser',
        'password': 'TestPassword123!'
    })
    assert response.status_code == 201  # ← CHANGE THIS TO 200
```

**Result**:
- Job 1 fails at pytest step
- Pipeline stops immediately
- No subsequent jobs run
- Email sent with pytest.xml and coverage.xml attached

**Why it fails**: The test expects status code 201 but gets 200, causing assertion to fail

---

### Scenario 2: Application Crash

**What to change**: Introduce a syntax error that crashes the app

**File**: `app/__init__.py`

**Change**:
```python
# Add this at the top of the file (after imports):
invalid_syntax_here  # ← ADD THIS LINE
```

**Result**:
- Job 1 fails during pytest (import error)
- Pipeline stops
- Email sent with error details

**Why it fails**: Python cannot import the app due to syntax error

---

## Job 2: Secrets Scan Failures

### Scenario 1: Hardcoded API Key

**What to change**: Add a real-looking API key to the code

**File**: `app/auth.py` (or any Python file in `app/`)

**Change**:
```python
# Add this anywhere in the file (e.g., after imports):
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE"  # ← ADD THIS LINE
# Or add a real-looking token:
GITHUB_TOKEN = "ghp_1234567890abcdef1234567890abcdef12345678"  # ← ADD THIS LINE
```

**Result**:
- Job 2 fails at Gitleaks step
- Gitleaks detects the secret pattern
- Pipeline stops
- Email sent with gitleaks-report.json attached

**Why it fails**: Gitleaks pattern matching detects AWS secret key or GitHub token pattern

---

### Scenario 2: Hardcoded Password

**What to change**: Add a hardcoded password

**File**: `app/auth.py`

**Change**:
```python
# Add this anywhere:
DATABASE_PASSWORD = "SuperSecretPassword123!"  # ← ADD THIS LINE
```

**Result**:
- Job 2 fails at Gitleaks step
- Gitleaks detects password pattern
- Pipeline stops

**Why it fails**: Gitleaks detects common password patterns

---

### Scenario 3: Private Key

**What to change**: Add a private key

**File**: Create new file `app/private_key.pem`

**Change**:
```pem
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAzK8vRZmZ2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y2Y
... (fake private key content) ...
-----END RSA PRIVATE KEY-----
```

**Result**:
- Job 2 fails at Gitleaks step
- Gitleaks detects private key pattern
- Pipeline stops

**Why it fails**: Gitleaks detects private key header/footer patterns

---

## Job 3: SAST Failures

### Scenario 1: SQL Injection (Semgrep)

**What to change**: Add SQL injection vulnerability

**File**: `app/auth.py`

**Change**:
```python
# Add this function to the file:
def get_user_by_id(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # ← VULNERABLE
    return db.session.execute(query)
```

**Result**:
- Job 3 fails at Semgrep step
- Semgrep detects SQL injection pattern
- Pipeline stops
- Email sent with semgrep-report.json attached

**Why it fails**: Semgrep rule detects f-string SQL queries with user input (ERROR severity)

---

### Scenario 2: Command Injection (Bandit)

**What to change**: Add command execution with user input

**File**: `app/auth.py`

**Change**:
```python
# Add this function:
def run_command(cmd):
    import os
    os.system(cmd)  # ← VULNERABLE - Bandit will detect this
```

**Result**:
- Job 3 fails at Bandit step
- Bandit detects use of `os.system()` (HIGH severity)
- Pipeline stops
- Email sent with bandit-report.json attached

**Why it fails**: Bandit detects use of dangerous functions like `os.system()`, `subprocess.call()` with shell=True

---

### Scenario 3: Hardcoded Secret (Bandit)

**What to change**: Add hardcoded secret

**File**: `app/auth.py`

**Change**:
```python
# Add this:
SECRET_KEY = "this-is-a-hardcoded-secret-key"  # ← VULNERABLE
```

**Result**:
- Job 3 fails at Bandit step
- Bandit detects hardcoded secret (HIGH severity)
- Pipeline stops

**Why it fails**: Bandit detects variables named "password", "secret", "key" with hardcoded values

---

### Scenario 4: Use of eval() (Bandit)

**What to change**: Add use of eval()

**File**: `app/auth.py`

**Change**:
```python
# Add this function:
def execute_code(code):
    return eval(code)  # ← VULNERABLE
```

**Result**:
- Job 3 fails at Bandit step
- Bandit detects use of `eval()` (HIGH severity)
- Pipeline stops

**Why it fails**: Bandit detects use of dangerous functions like `eval()`, `exec()`

---

### Scenario 5: Weak Cryptography (Semgrep)

**What to change**: Use weak MD5 hash

**File**: `app/auth.py`

**Change**:
```python
# Add this function:
def hash_password(password):
    import hashlib
    return hashlib.md5(password.encode()).hexdigest()  # ← VULNERABLE
```

**Result**:
- Job 3 fails at Semgrep step
- Semgrep detects use of weak hash (MD5, SHA1)
- Pipeline stops

**Why it fails**: Semgrep rule detects use of weak cryptographic algorithms

---

## Job 4: SCA Failures

### Scenario 1: Vulnerable Python Package

**What to change**: Add a package with known vulnerabilities

**File**: `requirements.txt`

**Change**:
```txt
# Add this line to requirements.txt:
flask==0.12.0  # ← OLD VERSION WITH KNOWN VULNERABILITIES
```

**Result**:
- Job 4 fails at pip-audit step
- pip-audit detects known CVEs in Flask 0.12.0
- Pipeline stops
- Email sent with pip-audit-report.json attached

**Why it fails**: pip-audit checks Python Package Index (PyPI) for known vulnerabilities

---

### Scenario 2: Outdated Package with Security Fix

**What to change**: Use an outdated version of a package

**File**: `requirements.txt`

**Change**:
```txt
# Change Flask version to an old one:
flask==1.0.0  # ← OLD VERSION
```

**Result**:
- Job 4 fails at pip-audit step
- pip-audit detects that newer version has security fixes
- Pipeline stops

**Why it fails**: pip-audit flags packages that have security updates available

---

### Scenario 3: Vulnerable Dependency in Dockerfile

**What to change**: Add a Dockerfile with vulnerable base image

**File**: Create `Dockerfile`

**Change**:
```dockerfile
FROM python:3.7-alpine  # ← OLD PYTHON VERSION WITH VULNERABILITIES
COPY requirements.txt .
RUN pip install -r requirements.txt
```

**Result**:
- Job 4 fails at Trivy step
- Trivy detects vulnerabilities in Python 3.7 base image
- Pipeline stops
- Email sent with trivy-fs-report.json attached

**Why it fails**: Trivy scans Dockerfiles and detects vulnerabilities in base images

---

## Job 5: SonarQube Failures

### Scenario 1: Low Code Coverage

**What to change**: Remove a test to lower coverage below 80%

**File**: `tests/test_auth.py`

**Change**:
```python
# Comment out or delete this test:
# def test_register_success(client):
#     response = client.post('/auth/register', json={
#         'username': 'testuser',
#         'password': 'TestPassword123!'
#     })
#     assert response.status_code == 201
```

**Result**:
- Job 5 fails at SonarQube quality gate
- Coverage drops below 80%
- Pipeline stops
- Email sent indicating quality gate failure

**Why it fails**: SonarQube quality gate requires ≥80% coverage on new code

---

### Scenario 2: Code Duplication

**What to change**: Add duplicated code

**File**: `app/auth.py`

**Change**:
```python
# Add this duplicated function twice:
def duplicate_function_1():
    return "This is a long string that will be detected as duplication"

def duplicate_function_2():
    return "This is a long string that will be detected as duplication"
```

**Result**:
- Job 5 fails at SonarQube quality gate
- SonarQube detects code duplication
- Pipeline stops

**Why it fails**: SonarQube quality gate has duplication threshold (typically 3-5%)

---

### Scenario 3: Code Smell (Complexity)

**What to change**: Add a complex function

**File**: `app/auth.py`

**Change**:
```python
# Add this complex function:
def complex_function(a, b, c, d, e, f, g, h, i, j):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            if g:
                                if h:
                                    if i:
                                        if j:
                                            return True
    return False
```

**Result**:
- Job 5 fails at SonarQube quality gate
- SonarQube detects high cognitive complexity
- Pipeline stops

**Why it fails**: SonarQube quality gate has complexity threshold (typically 15)

---

### Scenario 4: Unused Code

**What to change**: Add unused imports or variables

**File**: `app/auth.py`

**Change**:
```python
# Add unused import:
import os  # ← UNUSED IMPORT
```

**Result**:
- Job 5 may fail or show warning
- SonarQube detects unused code
- May fail depending on quality gate configuration

**Why it fails**: SonarQube flags unused code as code smell

---

## Job 6: DAST Failures

### Scenario 1: Missing Security Headers

**What to change**: Remove security headers from Flask app

**File**: `app/__init__.py`

**Change**:
```python
# Find the after_request function and comment out header setting:
@app.after_request
def after_request(response):
    # response.headers['X-Content-Type-Options'] = 'nosniff'  # ← COMMENT OUT
    # response.headers['X-Frame-Options'] = 'DENY'  # ← COMMENT OUT
    # response.headers['X-XSS-Protection'] = '1; mode=block'  # ← COMMENT OUT
    return response
```

**Result**:
- Job 6 fails at DAST step
- DAST check detects missing security headers
- Pipeline stops
- Email sent with dast-report.txt attached

**Why it fails**: DAST script checks for presence of security headers and fails if missing

---

### Scenario 2: Application Fails to Start

**What to change**: Break the application startup

**File**: `wsgi.py`

**Change**:
```python
# Add an error at the top:
raise Exception("Intentional startup failure")  # ← ADD THIS
```

**Result**:
- Job 6 fails at app startup step
- Application crashes during startup
- Pipeline stops
- Email sent with app.log attached

**Why it fails**: DAST job cannot start the application for scanning

---

### Scenario 3: Health Endpoint Fails

**What to change**: Break the health endpoint

**File**: `app/routes.py`

**Change**:
```python
# Find the health endpoint and make it fail:
@app.route('/health')
def health():
    return jsonify({'status': 'error'}), 500  # ← CHANGE TO 500 ERROR
```

**Result**:
- Job 6 fails at health check step
- curl command fails (non-zero exit code)
- Pipeline stops

**Why it fails**: DAST job runs `curl -f` which fails on HTTP errors

---

## Summary Table

| Job | What to Change | File | Why it Fails |
|-----|----------------|------|--------------|
| 1 | Change assertion from 201 to 200 | `tests/test_auth.py` | Test assertion fails |
| 1 | Add syntax error | `app/__init__.py` | Import error |
| 2 | Add API key | `app/auth.py` | Gitleaks detects secret |
| 2 | Add password | `app/auth.py` | Gitleaks detects password |
| 3 | Add SQL injection | `app/auth.py` | Semgrep detects ERROR severity |
| 3 | Use os.system() | `app/auth.py` | Bandit detects HIGH severity |
| 3 | Use eval() | `app/auth.py` | Bandit detects HIGH severity |
| 4 | Add Flask 0.12.0 | `requirements.txt` | pip-audit finds CVEs |
| 4 | Add old Docker base | `Dockerfile` | Trivy finds vulnerabilities |
| 5 | Remove test | `tests/test_auth.py` | Coverage < 80% |
| 5 | Add complex function | `app/auth.py` | Complexity too high |
| 6 | Remove security headers | `app/__init__.py` | Headers missing |
| 6 | Break startup | `wsgi.py` | App won't start |

---

## How to Restore

After testing any failure scenario, restore the file to its original state:

```bash
git checkout -- <filename>
```

Or use `git diff` to see what changed and revert manually:

```bash
git diff
```

Then commit and push to see the pipeline pass again.
