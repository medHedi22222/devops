# Demo Branches — GitHub Actions

Branches volontairement vulnérables pour montrer que la pipeline **bloque**.
**Ne jamais merger dans `master`.**

Workflow : `.github/workflows/devsecops.yml`

## Résumé

| Branche | Vulnérabilité | Job qui échoue | Outil |
|---------|---------------|----------------|-------|
| `demo/leaked-secret` | Fausse clé AWS / API | `2 · Secrets Scan` | Gitleaks |
| `demo/insecure-code` | `eval` / `exec` / MD5 | `3 · SAST` | Semgrep + Bandit |
| `demo/vulnerable-dependency` | `requests==2.6.0` | `4 · SCA` | Trivy FS / pip-audit |
| `demo/vulnerable-image` | `python:3.7-slim` | `5 · Docker Build & Scan` | Trivy image |
| `master` | — | aucun | SUCCESS |

## Comment démontrer

```bash
# Pousser les branches de démo
git push -u origin demo/leaked-secret
git push -u origin demo/insecure-code
git push -u origin demo/vulnerable-dependency
git push -u origin demo/vulnerable-image

# Puis ouvrir GitHub → Actions et montrer les runs rouges
# Enfin :
git push origin master   # run vert end-to-end
```

## Détail par branche

### 1. `demo/leaked-secret`
- Fichier : `app/demo_secrets.py` (clés **factices**)
- Attendu : Gitleaks exit ≠ 0 → job Secrets rouge

### 2. `demo/insecure-code`
- Fichier : `app/demo_insecure.py` (`eval`, `exec`, hash faible)
- Attendu : Semgrep et/ou Bandit bloquent le job SAST

### 3. `demo/vulnerable-dependency`
- `requirements.txt` pinne `requests==2.6.0` (CVE connues)
- Attendu : pip-audit / Trivy FS bloquent le job SCA

### 4. `demo/vulnerable-image`
- `Dockerfile` base `python:3.7-slim` (image obsolète)
- Attendu : Trivy image bloque après le build

## Run propre

Sur `master` sans ces fichiers / pins : tous les jobs jusqu’au scan Docker passent.
Push Docker Hub / Vercel uniquement si les secrets GitHub sont configurés
(sinon ces jobs sont skippés sans faire échouer la pipeline).

## Screenshots à garder

```
screenshots/
├── demo-branches/.../gha-failure.png
└── clean-run/gha-success.png
```
