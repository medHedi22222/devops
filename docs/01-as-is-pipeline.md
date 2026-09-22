# Pipeline As-Is (avant DevSecOps)

Baseline **sans** contrôles de sécurité — à comparer avec `02-to-be-pipeline.md`.

Implémentation : [`.github/workflows/as-is.yml`](../.github/workflows/as-is.yml)
(déclenchement manuel uniquement).

## Étapes

1. **Checkout** — git  
2. **Install** — pip (aucune vérif d’intégrité / CVE)  
3. **Unit tests** — pytest (pas de gate sécurité)  
4. **« Deploy »** — simulé, sans scan d’image ni secrets  

## Faiblesses (pourquoi ce n’est pas acceptable)

| Zone | Risque |
|------|--------|
| Dépendances | CVE non détectées |
| Secrets | Clés commitées non bloquées |
| Code | Pas de SAST (`eval`, debug, etc.) |
| Image Docker | Base vulnérable non scannée |
| Déploiement | Artefact non vérifié poussé en prod |

## Outils

Aucun scanner (Gitleaks, Semgrep, Bandit, Trivy, pip-audit).

Ce fichier sert de **référence avant** pour le rapport et la soutenance.
