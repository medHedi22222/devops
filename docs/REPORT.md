# Rapport de Projet DevSecOps

## Contexte

Projet universitaire : application Flask + JWT protégée par un pipeline CI/CD
**GitHub Actions** (DevSecOps / shift-left), image Docker (Docker Hub) et déploiement Vercel.

Jenkins a été écarté au profit de GitHub Actions pour une CI reproductible sur le
dépôt distant (pas de serveur Jenkins local, runners cloud avec Docker).

### Objectifs

1. Application Flask avec JWT
2. Pipeline CI/CD avec contrôles SAST / SCA / secrets / scan d’image
3. Quality gates bloquants (secrets, CRITICAL/HIGH)
4. Démos : branches vulnérables → pipeline rouge ; `master` propre → vert
5. Documentation en français

## Méthodologie

Phases : bootstrap → app + tests → Docker → pipeline as-is → shift-left
(pre-commit) → pipeline sécurisé (GHA) → quality gates → reporting → déploiement
→ branches demo → docs.

Secrets : `.env` (gitignore) + **GitHub Actions secrets** + variables Vercel.
Jamais de secret dans le dépôt.

## Outils et justification

| Outil | Rôle | Pourquoi |
|-------|------|----------|
| GitHub Actions | CI/CD | Intégré au repo, YAML versionné, Docker sur runner |
| Gitleaks | Secrets | Patterns AWS/GitHub/Slack, bloquant |
| Semgrep | SAST | Règles custom (`.semgrep/custom.yaml`) |
| Bandit | SAST Python | Complément Semgrep, HIGH+ bloquant |
| Trivy | SCA + image | CRITICAL/HIGH bloquants, images pinnées |
| pip-audit | SCA Python | CVE sur `requirements.txt` |
| Docker multi-stage | Artefact | Non-root, HEALTHCHECK, pas de secret dans l’image |
| Vercel | Runtime démo | Serverless Flask (`api/index.py`) |
| pre-commit | Shift-left | Gitleaks/Bandit/Semgrep avant push |

SonarQube reste optionnel en local (`infra/docker-compose.yml`) pour SonarLint.

## Intégration (pipeline to-be)

Fichier : `.github/workflows/devsecops.yml`

1. Install & Test — pytest + coverage (**bloquant**)
2. Secrets — Gitleaks (**bloquant**)
3. SAST — Semgrep + Bandit (**bloquant**)
4. SCA — Trivy FS + pip-audit (**bloquant** CRITICAL/HIGH)
5. Docker build & scan — Trivy image (**bloquant**)
6. Docker Hub — `master` si secrets présents
7. Vercel + smoke `/health` — `master` si secrets présents

Baseline as-is (sans sécu) : `.github/workflows/as-is.yml` (manuel).

## Résultats attendus (démo)

| Branche | Résultat | Job en échec |
|---------|----------|--------------|
| `demo/leaked-secret` | FAILED | Secrets (Gitleaks) |
| `demo/insecure-code` | FAILED | SAST |
| `demo/vulnerable-dependency` | FAILED | SCA |
| `demo/vulnerable-image` | FAILED | Docker scan |
| `master` | SUCCESS | — |

*(Insérer ici les captures d’écran GitHub Actions.)*

## Difficultés

1. **Jenkins local** — pulls Docker / infra instable → bascule vers GitHub Actions.
2. **Faux positifs Gitleaks** — exemples dans l’historique ; scan working-tree (`--no-git`) pour une démo fiable.
3. **CVE base image** — Trivy avec `--ignore-unfixed` pour ne bloquer que le corrigeable.
4. **Vercel filesystem** — SQLite sous `/tmp` (limitation acceptée pour la démo).

## Améliorations futures

- DAST (OWASP ZAP) sur un staging éphémère
- SBOM (Syft / CycloneDX)
- SonarCloud branché sur le workflow
- Vault / OIDC pour les secrets cloud
- Checkov étendu sur le compose

## Conclusion

Le projet démontre un pipeline DevSecOps **actionnable** : la CI refuse le code
dangereux et valide un `master` propre. L’application reste volontairement petite ;
la valeur est dans les **quality gates** et la traçabilité (artifacts de rapports).

Voir aussi : `01-as-is-pipeline.md`, `02-to-be-pipeline.md`, `QUALITY_GATES.md`,
`DEMO_BRANCHES.md`, `MANUAL_STEPS.md`.
