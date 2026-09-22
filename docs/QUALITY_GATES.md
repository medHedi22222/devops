# Quality Gates Documentation

This document defines the quality gates and thresholds for the GitHub Actions
CI/CD pipeline (`.github/workflows/devsecops.yml`), explaining the rationale behind each threshold.

## Quality Gate Philosophy

Our quality gates follow a risk-based approach:
- **CRITICAL/HIGH severity**: Block deployment (security risk too high)
- **MEDIUM/LOW severity**: Warn but don't block (allow delivery while tracking issues)
- **Any leaked secret**: Block immediately (credential compromise risk)
- **Code quality**: Track and improve over time (not blocking to avoid slowing delivery)

## Security Quality Gates

### 1. Secrets Scanning (Gitleaks)

**Threshold**: Any finding → **BLOCK**

**Rationale**:
- Leaked secrets are immediately exploitable
- Can lead to credential theft, unauthorized access, data breaches
- No acceptable level of risk for exposed secrets
- Requires immediate remediation

**OWASP Category**: A02:2021 – Cryptographic Failures

**CVSS Impact**: 10.0 (Critical) - secrets can lead to full system compromise

**Implementation**:
```groovy
if (gitleaksOutput.contains('"findings":[') && !gitleaksOutput.contains('"findings":[]')) {
    error 'Gitleaks found secrets - blocking pipeline'
}
```

### 2. SAST - Semgrep & Bandit

**Threshold**: CRITICAL/HIGH → **BLOCK**, MEDIUM/LOW → **WARN**

**Rationale**:
- **CRITICAL/HIGH**: Immediate security risks (SQL injection, XSS, auth bypass)
- **MEDIUM/LOW**: Important but not immediately exploitable; allows delivery while tracking

**OWASP Categories**:
- A03:2021 – Injection (SQLi, XSS, command injection)
- A01:2021 – Broken Access Control
- A05:2021 – Security Misconfiguration

**CVSS Threshold**: ≥ 7.0 for blocking (HIGH/CRITICAL)

**Implementation**:
```groovy
// CRITICAL/HIGH issues block the pipeline
// MEDIUM/LOW issues result in UNSTABLE status
```

### 3. SonarQube Quality Gate

**Threshold**: No new bugs, no new vulnerabilities, no new security hotspots, coverage ≥ 80% on new code

**Rationale**:
- **No new bugs**: Prevents quality regression
- **No new vulnerabilities**: Prevents security regression
- **No new security hotspots**: Ensures security issues are reviewed
- **Coverage ≥ 80%**: Ensures new code is well-tested

**SonarQube Gate Configuration**:
```yaml
Quality Gate:
  - New Bugs: 0
  - New Vulnerabilities: 0
  - New Security Hotspots: 0
  - Coverage on New Code: ≥ 80%
  - New Code Coverage: ≥ 80%
```

**Implementation**:
```groovy
waitForQualityGate abortPipeline: true
```

### 4. Dependency Scanning (Trivy)

**Threshold**: CRITICAL/HIGH (CVSS ≥ 7.0) → **BLOCK**, MEDIUM/LOW → **WARN**

**Rationale**:
- **CRITICAL/HIGH**: Known exploitable vulnerabilities in dependencies
- **MEDIUM/LOW**: Less severe; allow delivery while tracking for future updates

**OWASP Category**: A08:2021 – Software and Data Integrity Failures

**CVSS Threshold**: ≥ 7.0 for blocking

**Implementation**:
```groovy
if (criticalCount > 0 || highCount > 0) {
    error "Trivy found ${criticalCount} CRITICAL and ${highCount} HIGH vulnerabilities - blocking pipeline"
}
```

### 5. Container Scanning (Trivy)

**Threshold**: CRITICAL/HIGH (CVSS ≥ 7.0) → **BLOCK**, MEDIUM/LOW → **WARN**

**Rationale**:
- **CRITICAL/HIGH**: Vulnerabilities in base image or installed packages
- **MEDIUM/LOW**: Track for future image updates

**OWASP Category**: A05:2021 – Security Misconfiguration

**CVSS Threshold**: ≥ 7.0 for blocking

**Implementation**:
```groovy
if (criticalCount > 0 || highCount > 0) {
    error "Trivy image scan found ${criticalCount} CRITICAL and ${highCount} HIGH vulnerabilities - blocking pipeline"
}
```

### 6. DAST (OWASP ZAP)

**Threshold**: HIGH → **BLOCK**, MEDIUM/LOW → **WARN**

**Rationale**:
- **HIGH**: Runtime vulnerabilities accessible to attackers
- **MEDIUM/LOW**: Track for future remediation

**OWASP Categories**:
- A01:2021 – Broken Access Control
- A03:2021 – Injection
- A07:2021 – Identification and Authentication Failures

**CVSS Threshold**: ≥ 7.0 for blocking

**Implementation**:
```groovy
if (highCount > 0) {
    error "ZAP found ${highCount} HIGH severity issues - blocking pipeline"
}
```

## Non-Blocking Gates

### 1. IaC Scanning (Checkov)

**Threshold**: Non-blocking (WARN)

**Rationale**:
- Infrastructure-as-code issues are important but don't immediately block deployment
- Allows delivery while tracking infrastructure improvements

**Implementation**:
```groovy
catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
    // Run Checkov
}
```

### 2. SBOM Generation (Syft)

**Threshold**: Non-blocking (informational)

**Rationale**:
- SBOM is for compliance and tracking, not a security gate
- Important for supply chain transparency

**Implementation**:
```groovy
catchError(buildResult: 'SUCCESS', stageResult: 'SUCCESS') {
    // Generate SBOM
}
```

## Test Quality Gates

### Unit Tests

**Threshold**: Must pass → **BLOCK**

**Rationale**:
- Tests verify functionality; failures indicate broken code
- No acceptable level of test failure

**Implementation**:
```groovy
post {
    failure {
        error 'Tests failed - blocking pipeline'
    }
}
```

### Code Coverage

**Threshold**: ≥ 80% on new code → **BLOCK**

**Rationale**:
- Ensures new code is adequately tested
- 80% is industry standard for critical applications
- Prevents untested code from reaching production

**Implementation**:
```groovy
// Configured in SonarQube quality gate
```

## Gate Status Meanings

- **SUCCESS**: All gates passed, safe to proceed
- **FAILURE**: Blocking gate failed, pipeline stops
- **UNSTABLE**: Non-blocking gate failed, pipeline continues but marked as unstable
- **ABORTED**: Pipeline manually stopped

## Threshold Justification Summary

| Gate | Blocking Threshold | Rationale | CVSS Threshold |
|------|-------------------|------------|----------------|
| Secrets | Any finding | Immediate credential compromise risk | N/A |
| SAST | CRITICAL/HIGH | Immediate security risks | ≥ 7.0 |
| SonarQube | New bugs/vulnerabilities/hotspots, coverage < 80% | Quality and security regression | Varies |
| Dependencies | CRITICAL/HIGH | Known exploitable vulnerabilities | ≥ 7.0 |
| Container | CRITICAL/HIGH | Known exploitable vulnerabilities | ≥ 7.0 |
| DAST | HIGH | Runtime security risks | ≥ 7.0 |
| IaC | Non-blocking | Infrastructure improvements | N/A |
| SBOM | Non-blocking | Compliance and tracking | N/A |
| Tests | Any failure | Broken functionality | N/A |
| Coverage | < 80% on new code | Inadequate testing | N/A |

## Risk Acceptance Process

If a blocking gate must be bypassed:

1. **Document the risk**: Explain why bypass is necessary
2. **Get approval**: Security team or project lead approval required
3. **Set expiry**: Temporary bypass with review date (max 7 days)
4. **Create tracking issue**: Ensure the issue is tracked for resolution
5. **Document in EXEMPTIONS.md**: Add to exemption log

## Monitoring and Improvement

### Regular Review
- Review gate effectiveness quarterly
- Adjust thresholds based on security posture changes
- Track false positive rates
- Monitor pipeline success/failure rates

### Metrics to Track
- Pipeline success rate by gate
- Average time to resolve blocking issues
- False positive rate by scanner
- Security issue trend over time
- Coverage trend over time

### Continuous Improvement
- Reduce false positives through better tool configuration
- Add new gates as security requirements evolve
- Automate remediation where possible
- Improve developer education on security issues

## Emergency Overrides

In emergency situations (production outage, critical deadline):

1. **Temporary bypass**: Override specific gate for 24 hours
2. **Executive approval**: CTO or security director approval required
3. **Immediate review**: Schedule review within 24 hours
4. **Post-mortem**: Document why emergency bypass was needed
5. **Prevention**: Implement changes to prevent future emergencies

## Contact

For quality gate questions or requests:
- Security Team: security@example.com
- DevOps Team: devops@example.com
- Project Lead: project-lead@example.com