# Exemptions Documentation

This document describes the exemption process for false positives from security scanners.

## Exemption Process Overview

Exemptions should be used sparingly and only for legitimate false positives. All exemptions must be:
- Properly documented with justification
- Approved by a security team member or project lead
- Given an expiry date for review
- Tracked in the exemption log below

## When to Request an Exemption

Exemptions are appropriate when:
1. A tool flags a false positive (not actually a security issue)
2. The vulnerability is in a test or development-only component
3. The issue is mitigated by other security controls
4. The risk is accepted for a specific business reason

Exemptions are NOT appropriate when:
1. The security issue is real but fixing it is inconvenient
2. The issue is in production code
3. There's no clear mitigation strategy
4. The justification is "we'll fix it later"

## Exemption Approval Process

### Step 1: Verification
1. Confirm the finding is actually a false positive
2. Review the vulnerability details and impact
3. Consider if code refactoring could eliminate the issue

### Step 2: Documentation
Document the exemption with:
- Finding ID (CVE, rule ID, or scanner-specific ID)
- Affected component/package/version
- Clear justification for exemption
- Proposed expiry date (max 6 months)
- Risk acceptance rationale

### Step 3: Approval
- Submit exemption request to security team or project lead
- Get written approval (email, ticket, or PR approval)
- Document approver name and date

### Step 4: Implementation
Apply the appropriate suppression mechanism:
- **Gitleaks**: Add to `.gitleaks.toml` allowlist
- **Bandit**: Add `# nosec` comment with explanation
- **Semgrep**: Add `# nosemgrep: <rule-id>` comment with explanation
- **Trivy**: Add to `.trivyignore` with justification and expiry
- **SonarQube**: Mark as "Won't Fix" or "False Positive" with justification

### Step 5: Tracking
Add entry to the exemption log below for traceability.

## Suppression Mechanisms

### Gitleaks Allowlist
Add to `.gitleaks.toml`:
```toml
[allowlist]
paths = ['''path/to/file''']
regexes = ['''pattern''']
```

### Bandit Suppression
Add inline comment:
```python
result = some_risky_function()  # nosec - justification
```

### Semgrep Suppression
Add inline comment:
```python
result = some_risky_function()  # nosemgrep: rule-id - justification
```

### Trivy Ignore
Add to `.trivyignore`:
```
CVE-XXXX-XXXXX:package:version # justification | expiry: YYYY-MM-DD
```

### SonarQube Exemption
- Mark issue as "False Positive" or "Won't Fix" in SonarQube UI
- Add detailed justification in the issue comments

## Exemption Log

| Date | Finding ID | Component | Version | Scanner | Justification | Approver | Expiry Date | Status |
|------|------------|-----------|---------|---------|---------------|----------|-------------|--------|
| - | - | - | - | - | - | - | - | - |

*No active exemptions currently. All security findings should be addressed properly.*

## Expiry Review Process

1. Before expiry date, review if exemption is still needed
2. If no longer needed, remove suppression and update log
3. If still needed, extend expiry with new justification and approval
4. Mark expired exemptions in log with "Expired" status

## Governance

### Who Can Approve
- Security team lead
- Project technical lead
- DevOps engineer with security responsibility

### Approval Criteria
- Justification is clear and documented
- Risk is understood and accepted
- Expiry date is reasonable (max 6 months)
- Alternative solutions were considered

### Audit Trail
All exemptions are auditable through:
- Git history of suppression files
- This exemption log
- SonarQube issue history
- Pipeline records

## Emergency Exemptions

In emergency situations (production outage, critical deadline):
1. Apply temporary exemption with 7-day expiry
2. Get retrospective approval within 24 hours
3. Document emergency nature in justification
4. Schedule proper review before expiry

## Removing Exemptions

When removing an exemption:
1. Update this log to mark as "Removed"
2. Remove suppression from configuration files
3. Commit the changes
4. Verify the scanner no longer flags the issue
5. If the issue is still present, address it properly

## Contact

For exemption requests or questions:
- Security Team: security@example.com
- Project Lead: project-lead@example.com
- DevOps Team: devops@example.com
