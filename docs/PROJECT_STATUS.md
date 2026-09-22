# Project Status

## Pipeline choice

**GitHub Actions only** (Jenkins removed). Reason: reproducible CI on GitHub
without local Jenkins/Docker Hub pull issues; same DevSecOps gates for the demo.

## Done

- Flask + JWT app, pytest, Docker multi-stage, Vercel entrypoint
- Pre-commit + Semgrep custom rules + Makefile `scan-local`
- GHA secured pipeline: test → Gitleaks → Semgrep/Bandit → Trivy/pip-audit → image scan → optional Hub/Vercel
- GHA as-is workflow (manual) for before/after
- Demo branches for fail demos; docs in French

## What you must do

1. Push `master` + `demo/*` branches  
2. Open **Actions** and verify green/red as in `docs/DEMO_BRANCHES.md`  
3. Optionally add Docker Hub / Vercel secrets (`docs/MANUAL_STEPS.md`)  
4. Screenshots for `docs/REPORT.md`

## Definition of demo success

| Ref | Result |
|-----|--------|
| `master` | green |
| each `demo/*` | red at the expected job |
