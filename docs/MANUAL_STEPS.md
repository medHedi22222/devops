# Étapes manuelles (GitHub Actions)

Ce projet n’utilise **plus Jenkins**. Toute la CI/CD tourne sur **GitHub Actions**.
Les secrets ne doivent jamais être commités.

## 1. Secrets GitHub (Settings → Secrets and variables → Actions)

### Obligatoires pour un `master` vert (scans seuls)

Aucun secret n’est requis pour les jobs de test / Gitleaks / Semgrep / Bandit / Trivy.
Un push sur `master` propre doit déjà passer au vert.

### Optionnels — push Docker Hub (job 6)

| Secret | Valeur |
|--------|--------|
| `DOCKERHUB_USERNAME` | votre user Docker Hub |
| `DOCKERHUB_TOKEN` | Access Token (Account Settings → Security) |

Sans ces secrets, le job **skip** le push (notice dans les logs) — le pipeline reste vert.

### Optionnels — déploiement Vercel (job 7)

| Secret | Valeur |
|--------|--------|
| `VERCEL_TOKEN` | token Vercel |
| `VERCEL_ORG_ID` | id org (`vercel link`) |
| `VERCEL_PROJECT_ID` | id projet |
| `VERCEL_URL` | URL prod (ex. `https://xxx.vercel.app`) pour le smoke test `/health` |

### Variables d’environnement sur Vercel (dashboard)

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `JWT_ACCESS_TOKEN_EXPIRES=900`
- `DATABASE_URL` (optionnel → SQLite sous `/tmp` sur Vercel)

## 2. Activer Actions

Repository → **Actions** → autoriser les workflows s’ils sont désactivés.

## 3. Démo professeur (branches)

Les branches locales `demo/*` doivent être poussées :

```bash
git push -u origin demo/leaked-secret
git push -u origin demo/insecure-code
git push -u origin demo/vulnerable-dependency
git push -u origin demo/vulnerable-image
git push origin master
```

Puis dans **Actions**, montrer :

1. `master` → tous les jobs verts  
2. chaque `demo/*` → échec au job attendu  

## 4. SonarQube local (optionnel)

```bash
cd infra
docker compose up -d
# UI http://localhost:9000 (admin/admin au 1er login)
```

Pas branché à la CI cloud (pas de Jenkins). Utile pour SonarLint en local.

## 5. Captures d’écran pour le rapport

Pour chaque démo : run GitHub Actions rouge + rapport artifact.  
Pour `master` : run vert + (si configuré) image Docker Hub + `/health` Vercel.
