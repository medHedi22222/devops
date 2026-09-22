# Plan de Présentation — Défense Orale

## Structure (8–10 diapositives)

### 1. Titre
- Pipeline CI/CD DevSecOps — Flask + JWT
- GitHub Actions (SAST, SCA, secrets, scan image)
- Docker Hub + Vercel

### 2. Problématique
- Pipelines « classiques » sans scan → secrets / CVE / code dangereux en prod
- Besoin de **shift-left** et de seuils bloquants (OWASP Top 10)

### 3. Application
- Flask factory, JWT, SQLAlchemy, headers sécu
- Endpoints : `/health`, `/auth/register`, `/auth/login`, `/auth/me`
- Tests pytest (~80 %+ sur le flux auth)

### 4. Pipeline GitHub Actions
- As-is (manuel, sans sécu) vs to-be (`.github/workflows/devsecops.yml`)
- Jobs : Test → Gitleaks → Semgrep/Bandit → Trivy/pip-audit → Image → Hub/Vercel
- Diagramme Mermaid (voir `02-to-be-pipeline.md`)

### 5. Shift-left développeur
- pre-commit : Gitleaks, Bandit, Semgrep
- `make scan-local`
- Extensions VS Code (SonarLint, etc.)

### 6. Quality gates
- Secret → BLOCK
- CRITICAL/HIGH (CVSS ≥ 7) → BLOCK
- MEDIUM/LOW → suivi / non bloquant
- Justification dans `QUALITY_GATES.md`

### 7. Démo live (cœur de la note)
- `master` → run **vert**
- `demo/leaked-secret` → rouge (Gitleaks)
- `demo/insecure-code` → rouge (SAST)
- `demo/vulnerable-dependency` → rouge (SCA)
- `demo/vulnerable-image` → rouge (Trivy image)
- Montrer un artifact de rapport

### 8. Déploiement
- Image scannée puis push Docker Hub (si secrets)
- Code validé déployé sur Vercel + smoke `/health`
- Deux cibles, un même commit validé

### 9. Difficultés & apprentissages
- Remplacement de Jenkins par GitHub Actions (reproductibilité)
- Gestion des faux positifs / exemptions (`EXEMPTIONS.md`)
- Limite SQLite sur Vercel

### 10. Conclusion & perspectives
- Pipeline qui **refuse** le mauvais code et **accepte** le code propre
- Suite : ZAP DAST, SBOM, SonarCloud, Vault/OIDC

## Checklist avant la soutenance

1. Push `master` + 4 branches `demo/*`
2. Captures Actions (vert + 4 rouges)
3. README + `MANUAL_STEPS.md` à jour
4. Ne merger aucune branche demo
