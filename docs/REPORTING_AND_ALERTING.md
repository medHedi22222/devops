# Reporting and Alerting Documentation

This document explains the reporting structure, alerting mechanisms, and how to access security scan results.

## Report Generation

### Automated Report Generation

All security scanners generate reports in both JSON and HTML formats where applicable. Reports are:

1. **Generated during pipeline execution**
2. **Stored in the `reports/` directory**
3. **Archived as Jenkins artifacts**
4. **Published as HTML reports where applicable**

### Report Types

#### 1. Secrets Scanning Report (Gitleaks)
- **Format**: JSON
- **Location**: `reports/gitleaks-report.json`
- **Content**: List of found secrets with locations and severity
- **Access**: Jenkins artifacts panel

#### 2. SAST Reports

**Semgrep Report**
- **Format**: JSON
- **Location**: `reports/semgrep-report.json`
- **Content**: Security findings with rule IDs, severity, and code locations
- **Access**: Jenkins artifacts panel

**Bandit Report**
- **Format**: JSON
- **Location**: `reports/bandit-report.json`
- **Content**: Python security issues with CWE mappings
- **Access**: Jenkins artifacts panel

#### 3. SonarQube Report
- **Format**: HTML (web interface)
- **Location**: SonarQube server dashboard
- **Content**: Code quality metrics, security hotspots, bugs, vulnerabilities
- **Access**: SonarQube UI (http://localhost:9000)

#### 4. Dependency Scanning Report (Trivy)
- **Format**: JSON
- **Location**: `reports/trivy-fs-report.json`
- **Content**: Vulnerability findings in dependencies with CVSS scores
- **Access**: Jenkins artifacts panel

#### 5. IaC Scanning Report (Checkov)
- **Format**: JSON
- **Location**: `reports/checkov-report.json`
- **Content**: Infrastructure-as-code security issues
- **Access**: Jenkins artifacts panel

#### 6. Container Scanning Report (Trivy)
- **Format**: JSON
- **Location**: `reports/trivy-image-report.json`
- **Content**: Vulnerability findings in Docker image layers
- **Access**: Jenkins artifacts panel

#### 7. SBOM Report (Syft)
- **Format**: CycloneDX JSON
- **Location**: `reports/sbom.json`
- **Content**: Software Bill of Materials with all dependencies
- **Access**: Jenkins artifacts panel

#### 8. DAST Report (OWASP ZAP)
- **Format**: HTML and JSON
- **Location**: `reports/zap-report.html`, `reports/zap-report.json`
- **Content**: Dynamic security findings with risk ratings
- **Access**: Jenkins HTML Publisher report panel

#### 9. Test Coverage Report
- **Format**: HTML and XML
- **Location**: `htmlcov/index.html`, `coverage.xml`
- **Content**: Code coverage metrics and detailed coverage reports
- **Access**: Jenkins HTML Publisher report panel

## Accessing Reports

### Via Jenkins UI

1. **Navigate to build**: Click on build number in Jenkins dashboard
2. **Artifacts**: Click "Artifacts" on left sidebar to download JSON reports
3. **HTML Reports**: Click "Coverage Report" or "ZAP DAST Report" on left sidebar

### Via SonarQube UI

1. **Navigate to SonarQube**: http://localhost:9000
2. **Select project**: Click on "devsecops-flask" project
3. **View metrics**: Browse code quality, security hotspots, and vulnerability details

### Via Local Files

Reports are archived per build and can be accessed through:
- Jenkins workspace (during build execution)
- Jenkins artifacts (after build completion)
- Direct download from Jenkins UI

## Report Archiving

### Archival Strategy

- **Per-build archival**: Each build has its own set of reports
- **Retention policy**: Keep last 30 days of builds (configurable in Jenkins)
- **Fingerprinting**: Reports are fingerprinted for traceability
- **Cleanup**: Old reports are automatically cleaned up based on retention policy

### Jenkins Archival Configuration

```groovy
// Archive all reports
archiveArtifacts artifacts: "${REPORTS_DIR}/**/*", fingerprint: true

// Publish HTML reports
publishHTML(target: [
    reportDir: 'htmlcov',
    reportFiles: 'index.html',
    reportName: 'Coverage Report'
])
```

## Alerting Mechanisms

### Email Notifications

#### Configuration

Email notifications are configured in the Jenkins pipeline using the `emailext` plugin:

```groovy
emailext(
    subject: "SUCCESS: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER}",
    body: "<p>Pipeline completed successfully!</p>...",
    to: '$DEFAULT_RECIPIENTS',
    mimeType: 'text/html'
)
```

#### Email Triggers

- **SUCCESS**: All security gates passed
- **FAILURE**: Blocking security gate failed
- **UNSTABLE**: Non-blocking security issues found

#### Email Content

Each email includes:
- Job name and build number
- Git commit SHA
- Build duration
- Pipeline status
- Link to build URL
- Specific failure/unstable reasons

#### Manual Setup Required

1. **Configure SMTP in Jenkins**:
   - Navigate to Jenkins → Configure System
   - Configure "E-mail Notification" section
   - Set SMTP server, port, and authentication
   - Test email configuration

2. **Set recipients**:
   - Configure `$DEFAULT_RECIPIENTS` environment variable
   - Or specify recipients directly in pipeline

### Alternative Notification Methods

#### Slack Webhook (Alternative to Email)

Replace email with Slack notifications:

```groovy
slackSend(
    color: 'good',
    message: "Pipeline succeeded: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
    channel: '#devsecops'
)
```

#### Microsoft Teams Webhook (Alternative to Email)

```groovy
office365ConnectorSend(
    webhookUrl: '$TEAMS_WEBHOOK_URL',
    status: 'Success',
    message: "Pipeline succeeded: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
)
```

## Trend Analysis

### SonarQube Trends

SonarQube automatically tracks:
- Code quality metrics over time
- Security hotspots trend
- Vulnerability trend
- Coverage trend
- Technical debt trend

**Access**: SonarQube project dashboard → "Measures" tab

### Custom Trend Tracking

For scan results not tracked by SonarQube:

#### Simple CSV Tracking Script

```bash
#!/bin/bash
# Track security scan trends

echo "date,build,critical,high,medium,low" > security-trends.csv

# Extract counts from Trivy report
critical=$(jq '.Results.Results[].Vulnerabilities | map(select(.Severity == "CRITICAL")) | length' reports/trivy-fs-report.json)
high=$(jq '.Results.Results[].Vulnerabilities | map(select(.Severity == "HIGH")) | length' reports/trivy-fs-report.json)
medium=$(jq '.Results.Results[].Vulnerabilities | map(select(.Severity == "MEDIUM")) | length' reports/trivy-fs-report.json)
low=$(jq '.Results.Results[].Vulnerabilities | map(select(.Severity == "LOW")) | length' reports/trivy-fs-report.json)

echo "$(date),${BUILD_NUMBER},${critical},${high},${medium},${low}" >> security-trends.csv
```

#### Integration Options

- **ELK Stack**: Send scan results to Elasticsearch for visualization
- **Grafana**: Create dashboards for security metrics
- **Prometheus**: Export metrics for monitoring
- **Custom Dashboard**: Build custom reporting dashboard

## Report Structure

### Directory Structure

```
reports/
├── gitleaks-report.json          # Secrets scanning
├── semgrep-report.json           # SAST (Semgrep)
├── bandit-report.json            # SAST (Bandit)
├── trivy-fs-report.json          # Dependency scanning
├── checkov-report.json           # IaC scanning
├── trivy-image-report.json       # Container scanning
├── sbom.json                     # Software Bill of Materials
├── zap-report.html               # DAST (HTML)
├── zap-report.json               # DAST (JSON)
├── coverage.xml                  # Test coverage (XML)
└── security-trends.csv           # Trend tracking (optional)
```

### JSON Report Format Example

Most scanners produce JSON in similar format:

```json
{
  "version": "1.0",
  "results": [
    {
      "ruleId": "python.flask.security.debug.enabled",
      "severity": "ERROR",
      "message": "Flask debug mode is enabled in production",
      "location": {
        "path": "app/__init__.py",
        "lines": {
          "start": 15,
          "end": 15
        }
      }
    }
  ]
}
```

## Report Analysis

### Quick Analysis

Use Jenkins UI to quickly identify:
- **Failed stages**: Red indicators in pipeline view
- **Unstable stages**: Yellow indicators in pipeline view
- **Report availability**: Check artifacts panel

### Detailed Analysis

1. **Download reports** from Jenkins artifacts
2. **Open JSON reports** in text editor or JSON viewer
3. **Review HTML reports** in browser
4. **Cross-reference findings** across different scanners
5. **Prioritize remediation** based on severity and exploitability

### Common Patterns

Look for these patterns in reports:
- **Repeated findings**: Same issue across multiple files
- **Trend deterioration**: Increasing vulnerability counts
- **False positive clusters**: Similar issues that may need exemption
- **High-risk components**: Packages/files with many findings

## Notification Configuration

### Jenkins System Configuration

1. **Navigate to** Jenkins → Configure System
2. **Configure**:
   - E-mail Notification (SMTP settings)
   - Slack Plugin (if using Slack)
   - Office 365 Connector (if using Teams)
3. **Test** notification configuration

### Pipeline Configuration

The pipeline uses environment variables for notification targets:
- `$DEFAULT_RECIPIENTS`: Email recipients
- `$SLACK_CHANNEL`: Slack channel (if configured)
- `$TEAMS_WEBHOOK_URL`: Teams webhook URL (if configured)

## Troubleshooting

### Reports Not Generated

1. **Check scanner execution**: Review stage logs
2. **Verify report directory**: Ensure `reports/` directory exists
3. **Check permissions**: Ensure Jenkins has write permissions
4. **Review scanner errors**: Check for scanner-specific errors

### Notifications Not Sent

1. **Verify SMTP configuration**: Test email in Jenkins configuration
2. **Check recipient settings**: Verify `$DEFAULT_RECIPIENTS` is set
3. **Review Jenkins logs**: Check for email-related errors
4. **Test manually**: Send test email from Jenkins configuration

### HTML Reports Not Published

1. **Install HTML Publisher plugin**: Ensure plugin is installed
2. **Check report paths**: Verify paths in `publishHTML` step
3. **Review plugin logs**: Check HTML Publisher plugin logs
4. **Verify file existence**: Ensure HTML files are generated

## Best Practices

1. **Review reports regularly**: Don't wait for failures
2. **Track trends**: Monitor improvement over time
3. **Prioritize findings**: Focus on high/critical severity
4. **Document false positives**: Use EXEMPTIONS.md process
5. **Share insights**: Discuss findings with team
6. **Automate analysis**: Consider automated report analysis
7. **Integrate with issue tracking**: Create tickets for findings
8. **Maintain retention**: Balance storage needs with analysis needs

## Future Enhancements

Potential improvements to reporting and alerting:

1. **Automated ticket creation**: Auto-create Jira tickets for findings
2. **Slack integration**: Rich Slack notifications with report snippets
3. **Dashboard integration**: Grafana dashboards for security metrics
4. **PDF reports**: Generate PDF summary reports
5. **Executive summaries**: High-level reports for management
6. **Compliance reports**: Generate compliance-specific reports
7. **Cost analysis**: Track remediation costs and time
8. **Predictive analytics**: Predict future security issues based on trends