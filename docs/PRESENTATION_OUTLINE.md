# Plan de Présentation - Défense Orale

## Structure de la Présentation (8-10 diapositives)

### Diapositive 1: Titre et Introduction

**Titre**: Implémentation d'un Pipeline CI/CD DevSecOps pour Application Flask

**Contenu**:
- Nom du projet
- Contexte du cours universitaire
- Objectifs principaux
- Votre nom et rôle

**Points clés**:
- Pipeline CI/CD sécurisé avec contrôles DevSecOps
- Application Flask avec authentification JWT
- Intégration de 8 outils de sécurité
- Déploiement dual Docker Hub + Vercel

---

### Diapositive 2: Contexte et Problématique

**Titre**: Pourquoi DevSecOps?

**Contenu**:
- Évolution des menaces de sécurité
- Limites des pipelines CI/CD traditionnels
- Besoin de shift-left security
- OWASP Top 10 comme référence

**Problématique**:
Comment intégrer efficacement les contrôles de sécurité dans un pipeline CI/CD sans impacter la vélocité de livraison?

**Points clés**:
- Sécurité intégrée, pas ajoutée à la fin
- Détection précoce = correction moins coûteuse
- Automatisation des contrôles de sécurité

---

### Diapositive 3: Architecture de l'Application

**Titre**: Application Flask avec Authentification JWT

**Contenu**:
- Architecture de l'application (diagramme)
- Composants principaux:
  - Flask app factory pattern
  - JWT authentication
  - SQLAlchemy ORM
  - Security headers
- Endpoints API:
  - GET /health
  - POST /auth/register
  - POST /auth/login
  - GET /auth/me

**Points clés**:
- Application simple mais sécurisée
- Tests unitaires avec 85% de couverture
- Pas de secrets hardcodés
- Validation des entrées

---

### Diapositive 4: Pipeline CI/CD - Vue d'Ensemble

**Titre**: Pipeline DevSecOps à 14 Étapes

**Contenu**:
- Diagramme du pipeline complet (Mermaid)
- 14 étapes du pipeline:
  1. Checkout
  2. Install & Test
  3. Secrets Scan (Gitleaks)
  4. SAST (Semgrep, Bandit, SonarQube)
  5. Quality Gate
  6. Dependency Scan (Trivy)
  7. IaC Scan (Checkov)
  8. Docker Build
  9. Docker Scan (Trivy)
  10. SBOM (Syft)
  11. Deploy Staging
  12. DAST (OWASP ZAP)
  13. Docker Push
  14. Vercel Deploy

**Points clés**:
- Pipeline déclaratif Jenkins
- Contrôles de sécurité à chaque étape
- Quality gates basés sur le risque

---

### Diapositive 5: Outils de Sécurité - Shift-left

**Titre**: Outils Côté Développeur

**Contenu**:
- Pre-commit hooks:
  - Gitleaks (secrets)
  - Bandit (Python SAST)
  - Semgrep (SAST personnalisé)
  - Hooks d'hygiène (trailing whitespace, etc.)
- IDE Extensions:
  - SonarLint (quality + security)
  - Semgrep (security rules)
  - Python extensions
- Custom Semgrep Rules:
  - Flask debug enabled
  - Hardcoded secrets
  - Weak password hashing
  - SQL injection patterns

**Points clés**:
- Détection avant commit
- Feedback immédiat
- Réduction du temps de cycle

---

### Diapositive 6: Outils de Sécurité - Pipeline

**Titre**: Outils Intégrés dans le Pipeline

**Contenu**:
- SAST:
  - Semgrep (custom + auto rules)
  - Bandit (Python-specific)
  - SonarQube (code quality + security)
- SCA:
  - Trivy (dependencies + container)
- DAST:
  - OWASP ZAP (runtime security)
- Other:
  - Gitleaks (secrets scanning)
  - Checkov (IaC scanning)
  - Syft (SBOM generation)

**Points clés**:
- Versions Docker pinnées
- Rapports JSON + HTML
- Archivage et traçabilité

---

### Diapositive 7: Quality Gates et Résultats

**Titre**: Critères de Qualité et Résultats

**Contenu**:
- Quality Gates:
  - CRITICAL/HIGH (CVSS ≥ 7.0) → BLOCK
  - MEDIUM/LOW → WARN (UNSTABLE)
  - Secrets → BLOCK
  - SonarQube: 0 new bugs/vulnerabilities, coverage ≥ 80%
- Résultats:
  - 17 tests unitaires, 100% réussite
  - 0 secrets détectés (master)
  - 0 vulnérabilités critic/high
  - Quality gate SonarQube passé
- Démo Branches:
  - demo/leaked-secret → Gitleaks BLOCK
  - demo/vulnerable-dependency → Trivy BLOCK
  - demo/insecure-code → Semgrep/Bandit BLOCK
  - demo/vulnerable-image → Trivy BLOCK

**Points clés**:
- Seuils basés sur le risque
- Détection effective des vulnérabilités
- Pipeline master vert end-to-end

---

### Diapositive 8: Déploiement et Monitoring

**Titre**: Stratégie de Déploiement Dual

**Contenu**:
- Docker Hub:
  - Image scannée et validée
  - Tags: <commit-sha> et latest
  - Push uniquement après validation
- Vercel:
  - Déploiement serverless
  - Base de données éphémère (/tmp)
  - Variables d'environnement sécurisées
- Reporting:
  - Rapports JSON archivés
  - Rapports HTML publiés
  - Email notifications (SUCCESS/FAILURE/UNSTABLE)
  - SonarQube dashboard

**Points clés**:
- Double cible de déploiement
- Validation identique pour les deux
- Monitoring et alerting

---

### Diapositive 9: Difficultés et Améliorations

**Titre**: Leçons Apprises et Perspectives

**Contenu**:
- Difficultés rencontrées:
  - Configuration de l'environnement de test
  - Adaptation pour Vercel (filesystem éphémère)
  - Intégration de 8 outils différents
  - Gestion des exemptions
- Améliorations futures:
  - IaC scan étendu (docker-compose, Jenkins)
  - HashiCorp Vault pour secrets
  - Runtime security (Falco, Aqua)
  - ELK Stack + Grafana dashboards
  - Mutation testing
  - Automated dependency updates

**Points clés**:
- Processus d'apprentissage continu
- Améliorations basées sur les besoins
- Scalabilité de l'approche

---

### Diapositive 10: Conclusion

**Titre**: Conclusion et Questions

**Contenu**:
- Résumé des réalisations:
  - Pipeline DevSecOps complet et fonctionnel
  - 8 outils de sécurité intégrés
  - Quality gates robustes
  - Documentation complète
- Impact DevSecOps:
  - Shift-left security effectif
  - Automatisation des contrôles
  - Traçabilité complète
  - Amélioration continue
- Questions ouvertes

**Points clés**:
- Pipeline prêt pour production
- Base solide pour améliorations futures
- Modèle réutilisable pour d'autres applications

---

## Conseils pour la Présentation

### Préparation

1. **Entraînement**: Pratiquez la présentation plusieurs fois
2. **Timing**: Visez 10-12 minutes pour les 8-10 diapositives
3. **Screenshots**: Préparez des screenshots du pipeline Jenkins, rapports, et déploiements
4. **Demo**: Si possible, montrez une démo live du pipeline

### Pendant la Présentation

1. **Clarté**: Parlez clairement et à un rythme modéré
2. **Focus**: Concentrez-vous sur la valeur ajoutée de DevSecOps
3. **Exemples**: Utilisez les branches demo pour illustrer
4. **Questions**: Soyez prêt à répondre aux questions techniques

### Questions Anticipées

1. **Pourquoi ces outils spécifiques?**
   - Réponse: Justification basée sur les besoins, maturité, et intégration

2. **Comment gérer les faux positifs?**
   - Réponse: Processus d'exemption documenté dans EXEMPTIONS.md

3. **Impact sur la vélocité de livraison?**
   - Réponse: Shift-left réduit le temps global, quality gates basés sur le risque

4. **Coût de cette infrastructure?**
   - Réponse: Jenkins (auto-hébergé), Docker Hub (free tier), Vercel (free tier)

5. **Adaptation à d'autres applications?**
   - Réponse: Approche modulaire et documentée, facilement adaptable

### Ressources à Montrer

1. **Repository GitHub**: Montrez la structure du projet
2. **Jenkins Pipeline**: Montrez l'exécution du pipeline
3. **Rapports de Sécurité**: Montrez quelques rapports clés
4. **SonarQube Dashboard**: Montrez les métriques de qualité
5. **Documentation**: Mettez en avant la documentation complète

## Timing Suggéré

- Diapositive 1: 1 minute
- Diapositive 2: 1.5 minutes
- Diapositive 3: 1.5 minutes
- Diapositive 4: 2 minutes
- Diapositive 5: 1.5 minutes
- Diapositive 6: 1.5 minutes
- Diapositive 7: 2 minutes
- Diapositive 8: 1.5 minutes
- Diapositive 9: 1.5 minutes
- Diapositive 10: 1 minute + Questions

**Total**: ~15 minutes (présentation) + 5-10 minutes (questions)