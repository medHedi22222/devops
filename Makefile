.PHONY: help test scan scan-local dast-local clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

test: ## Run tests with coverage
	pytest --cov=app --cov-report=xml --cov-report=html

scan-local: ## Run all security scans locally
	@echo "Running Gitleaks..."
	gitleaks detect --source . --verbose --report-path reports/gitleaks-report.json --report-format json || true
	@echo "Running Bandit..."
	bandit -r app -f json -o reports/bandit-report.json || true
	@echo "Running Semgrep..."
	semgrep --config=.semgrep --json --output reports/semgrep-report.json app || true
	@echo "Running Trivy filesystem scan..."
	trivy fs --format json --output reports/trivy-fs-report.json . || true
	@echo "Security scans completed. Check reports/ directory."

dast-local: ## Run DAST scan locally with OWASP ZAP (requires app running on localhost:5000)
	@echo "Running OWASP ZAP DAST scan..."
	@echo "Make sure the Flask app is running on http://localhost:5000"
	docker run --rm -v "$$PWD:/zap/wrk" -t zaproxy/zap-stable:2.15.0 zap-baseline.py -t http://localhost:5000 -r reports/zap-report.html -x reports/zap-report.xml --alertLevel HIGH --no-progress || true
	@echo "DAST scan completed. Check reports/zap-report.html"

clean: ## Clean up generated files
	rm -rf reports/*
	rm -rf htmlcov/
	rm -f coverage.xml
	rm -rf .pytest_cache/
