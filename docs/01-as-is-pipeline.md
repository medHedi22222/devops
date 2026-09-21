# As-is Pipeline Documentation

## Overview
This document describes the state of the CI/CD pipeline **before** implementing DevSecOps security controls. This represents the "as-is" baseline for comparison with the "to-be" secured pipeline.

## Pipeline Stages

### 1. Checkout
- **Tool**: Git (Jenkins checkout step)
- **Purpose**: Retrieve source code from repository
- **Security Concerns**: None inherent, but no validation of repository integrity

### 2. Install
- **Tool**: pip (Python package manager)
- **Purpose**: Install application and development dependencies
- **Security Concerns**: 
  - No verification of dependency integrity
  - No vulnerability scanning of dependencies
  - Dependencies could contain known vulnerabilities (CVEs)
  - No dependency version pinning validation

### 3. Unit Tests
- **Tool**: pytest with coverage
- **Purpose**: Run automated tests and generate coverage report
- **Security Concerns**:
  - No security-focused testing
  - No input validation testing
  - No authentication flow security testing
  - Coverage report not used for quality gates

### 4. Build Image
- **Tool**: Docker
- **Purpose**: Build container image from Dockerfile
- **Security Concerns**:
  - No scanning of base image for vulnerabilities
  - No scanning of final image for vulnerabilities
  - No validation of Dockerfile security best practices
  - No secrets scanning in build context
  - No SBOM (Software Bill of Materials) generation

### 5. Deploy
- **Tool**: Placeholder (no actual deployment)
- **Purpose**: Deploy application (placeholder in as-is state)
- **Security Concerns**:
  - No pre-deployment security validation
  - No DAST (Dynamic Application Security Testing)
  - No runtime security monitoring
  - No environment variable validation

## Security Weaknesses Summary

### 1. No Secrets Scanning
- **Risk**: Secrets (API keys, passwords, tokens) could be committed to repository
- **Impact**: Credential theft, unauthorized access
- **OWASP Category**: A02:2021 – Cryptographic Failures

### 2. No SAST (Static Application Security Testing)
- **Risk**: Code vulnerabilities (SQL injection, XSS, etc.) go undetected
- **Impact**: Application compromise, data breaches
- **OWASP Category**: A03:2021 – Injection, A05:2021 – Security Misconfiguration

### 3. No SCA (Software Composition Analysis)
- **Risk**: Vulnerable dependencies with known CVEs
- **Impact**: Supply chain attacks, known exploit vulnerabilities
- **OWASP Category**: A08:2021 – Software and Data Integrity Failures

### 4. No Container Scanning
- **Risk**: Vulnerable base images and container layers
- **Impact**: Container escape, privilege escalation
- **OWASP Category**: A05:2021 – Security Misconfiguration

### 5. No DAST (Dynamic Application Security Testing)
- **Risk**: Runtime vulnerabilities undetected
- **Impact**: Attack surface exposure in production
- **OWASP Category**: A01:2021 – Broken Access Control

### 6. No Quality Gates
- **Risk**: Poor quality code can be deployed
- **Impact**: Technical debt, maintainability issues, potential security bugs
- **OWASP Category**: A04:2021 – Insecure Design

### 7. No Code Quality Analysis
- **Risk**: Code smells, duplication, complexity issues
- **Impact**: Maintenance burden, bug introduction
- **OWASP Category**: A04:2021 – Insecure Design

### 8. No IaC Scanning
- **Risk**: Infrastructure misconfigurations
- **Impact**: Security misconfigurations in deployment infrastructure
- **OWASP Category**: A05:2021 – Security Misconfiguration

### 9. No Notification System
- **Risk**: Pipeline failures go unnoticed
- **Impact**: Delayed response to security issues
- **OWASP Category**: A07:2021 – Identification and Authentication Failures

### 10. No Traceability/Reporting
- **Risk**: No audit trail of security findings
- **Impact**: Inability to track security improvements over time
- **OWASP Category**: A09:2021 – Security Logging and Monitoring Failures

## Tools Used in As-is Pipeline
- **Git**: Source code management
- **pip**: Python package management
- **pytest**: Testing framework
- **Docker**: Containerization

## Comparison with To-be Pipeline
The "to-be" pipeline will address all these weaknesses by implementing:
- Gitleaks for secrets scanning
- Semgrep and Bandit for SAST
- Trivy and pip-audit for SCA
- Trivy for container scanning
- OWASP ZAP for DAST
- SonarQube for code quality and security hotspots
- Quality gates with blocking thresholds
- Comprehensive reporting and notification system

## Conclusion
The as-is pipeline represents a traditional CI/CD approach focused on functionality rather than security. While it successfully builds and tests the application, it lacks essential security controls that could prevent vulnerabilities from reaching production. The transformation to a DevSecOps pipeline will shift security left, making it an integral part of the development lifecycle.
