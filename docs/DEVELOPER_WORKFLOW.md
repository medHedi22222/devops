# Developer Workflow - Shift-left Security

This document explains the developer-side security tools and how to use them effectively in the development workflow.

## Pre-commit Hooks Installation

### Step 1: Install pre-commit
```bash
pip install pre-commit
```

### Step 2: Install the hooks
```bash
pre-commit install
```

This installs git hooks that will run automatically before each commit.

### Step 3: Run hooks manually (optional)
```bash
# Run on all files
pre-commit run --all-files

# Run on staged files only
pre-commit run
```

## Security Tools Explanation

### 1. Gitleaks - Secrets Detection
**Purpose**: Detects hardcoded secrets, API keys, passwords, and tokens in code.

**What it detects**:
- AWS access keys (AKIA...)
- GitHub tokens
- API keys
- Database connection strings
- Private keys
- JWT secrets

**Vulnerability Class**: A02:2021 – Cryptographic Failures (OWASP Top 10)

**What to do if flagged**:
1. Remove the secret from code
2. Rotate the secret if it was committed to a public repository
3. Use environment variables or secret management tools
4. Add to `.gitleaks.toml` allowlist only if it's a false positive with proper justification

### 2. Bandit - Python SAST
**Purpose**: Static analysis tool for Python security issues.

**What it detects**:
- Use of unsafe functions (exec, eval)
- Hardcoded passwords
- Weak cryptographic algorithms
- SQL injection risks
- Shell injection risks

**Vulnerability Classes**:
- A03:2021 – Injection (SQLi, command injection)
- A02:2021 – Cryptographic Failures
- A05:2021 – Security Misconfiguration

**What to do if flagged**:
1. Review the security issue
2. Use safer alternatives (e.g., parameterized queries instead of string concatenation)
3. Add `# nosec` comment only if you have a valid security reason and document it

### 3. Semgrep - Custom Security Rules
**Purpose**: Security-focused static analysis with custom rules for this project.

**Custom rules in `.semgrep/custom.yaml`**:
- `flask-debug-enabled`: Detects Flask debug mode in production
- `hardcoded-secret-key`: Detects hardcoded Flask secret keys
- `hardcoded-jwt-secret`: Detects hardcoded JWT secrets
- `weak-password-hash`: Detects weak password hashing (MD5)
- `sql-injection-string-format`: Detects SQL injection via string concatenation
- `eval-user-input`: Detects dangerous eval() with user input
- `exec-user-input`: Detects dangerous exec() with user input
- `insecure-deserialization`: Detects unsafe pickle deserialization
- `hardcoded-api-key`: Detects hardcoded API keys
- `weak-token-expiry`: Warns about JWT token expiry time

**Vulnerability Classes**:
- A03:2021 – Injection
- A02:2021 – Cryptographic Failures
- A08:2021 – Software and Data Integrity Failures
- A05:2021 – Security Misconfiguration

**What to do if flagged**:
1. Review the specific security issue
2. Follow the suggested fix in the rule
3. Add `# nosemgrep` comment only with justification

### 4. Basic Hygiene Hooks
**Purpose**: Code quality and basic security checks.

**What they detect**:
- Trailing whitespace
- Missing newlines at end of files
- Large files (potential data leakage)
- Private keys in code
- Merge conflicts
- Invalid YAML/JSON/TOML syntax
- Mixed line endings

**What to do if flagged**:
1. Most of these are auto-fixable
2. Remove private keys immediately
3. Resolve merge conflicts before committing

### 5. Code Quality Tools
**Purpose**: Ensure code quality and consistency.

**Tools**:
- **Black**: Python code formatter (enforces PEP 8)
- **Flake8**: Python style guide enforcement

**What to do if flagged**:
1. Run `black app/` to auto-format code
2. Fix Flake8 warnings manually or use auto-fix

## IDE Integration

### VS Code Extensions
The recommended extensions in `.vscode/extensions.json` include:

1. **SonarLint**: Real-time code quality and security analysis
   - Connects to SonarQube server for consistent rules
   - Shows security hotspots and bugs inline

2. **Semgrep**: Security-focused static analysis
   - Runs custom security rules
   - Detects vulnerabilities in real-time

3. **Python extensions**: Language support, linting, formatting

4. **Docker extension**: Container file support and validation

### Using SonarLint Connected Mode
1. Install SonarLint extension
2. Configure connection to SonarQube server
3. Bind project to SonarQube project
4. Get real-time feedback matching server rules

## Running All Checks Locally

### Before pushing code
```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Run tests with coverage
pytest --cov=app --cov-report=xml

# Run all security scans
make scan-local
```

### What happens on push
If any security check fails:
1. The commit will be blocked
2. You'll see detailed error messages
3. Fix the issues and try again

## Continuous Integration Integration

These same tools run in the Jenkins pipeline with stricter thresholds:
- **Blocking**: Any secret found, high/critical security issues
- **Warning**: Medium/low security issues (pipeline becomes UNSTABLE)
- **Non-blocking**: Code quality issues (logged but don't block)

## False Positive Management

If a tool flags a false positive:

1. **Verify it's truly a false positive**
2. **Document the reason**
3. **Use appropriate suppression**:
   - Gitleaks: Add to `.gitleaks.toml` allowlist
   - Bandit: Add `# nosec` comment with explanation
   - Semgrep: Add `# nosemgrep` comment with explanation
   - Trivy: Add to `.trivyignore` with justification and expiry

4. **Track in EXEMPTIONS.md** with:
   - Date
   - Finding ID
   - Justification
   - Approver
   - Expiry date

## Benefits of Shift-left Security

1. **Early Detection**: Find vulnerabilities before they reach CI/CD
2. **Faster Feedback**: Get immediate feedback in the IDE
3. **Reduced Costs**: Fix vulnerabilities during development, not in production
4. **Developer Education**: Learn security best practices through tool feedback
5. **Consistent Standards**: Same tools in development and CI/CD

## Troubleshooting

### Pre-commit hooks not running
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### Tools not found
```bash
# Install dependencies
pip install -r requirements-dev.txt
```

### False positives overwhelming
1. Review and document legitimate exemptions
2. Consider if code needs refactoring
3. Update tool configuration if rules are too strict

## Best Practices

1. **Never ignore security warnings** without investigation
2. **Run pre-commit hooks before pushing** to save time
3. **Use IDE extensions** for real-time feedback
4. **Document exemptions** properly with justification
5. **Keep tools updated** to benefit from latest security rules
6. **Review security findings** regularly, not just when forced
