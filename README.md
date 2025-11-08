# 🚀 B2B Lead Generation API

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)

Une API REST complète et conforme RGPD pour la génération de leads B2B via scraping légal de sources publiques françaises.

## ⚠️ Avertissements Légaux

### ✅ Pratiques Légales
- ✅ Scraping de **données publiques uniquement** (annuaires professionnels)
- ✅ Respect strict de **robots.txt**
- ✅ **Rate limiting** pour éviter la surcharge des serveurs
- ✅ **User-Agent identifié** (LeadGenBot/1.0)
- ✅ **Conformité RGPD** complète (consentement, opt-out, minimisation)
- ✅ **Rétention limitée** des données (3 ans maximum)

### ❌ Interdictions Strictes
- ❌ **LinkedIn scraping INTERDIT** (violation des TOS + risques légaux)
- ❌ Scraping de sites interdisant explicitement la collecte
- ❌ Collecte de données personnelles sensibles
- ❌ Utilisation pour spam ou harcèlement

## 🎯 Fonctionnalités

### Core Features
- 🔍 **Scraping multi-sources** : PagesJaunes, Kompass, Societe.com
- ✉️ **Vérification d'emails** : Validation DNS MX + SMTP
- 🌍 **Filtrage géographique** : Recherche par coordonnées GPS + rayon (PostGIS)
- 📊 **Scoring de qualité** : Score de confiance 0-1 pour chaque lead
- 🔄 **Jobs asynchrones** : Traitement en arrière-plan avec Celery
- 📤 **Export** : CSV et JSON

### RGPD & Sécurité
- 🔒 **Authentification** : Clé API
- 👤 **Gestion des consentements** : Opt-out et suppression des données
- 📋 **Audit logs** : Traçabilité complète
- 🗑️ **Suppression automatique** : Données > 3 ans
- 🔐 **Chiffrement** : Données sensibles protégées

## 📋 Prérequis

- Docker & Docker Compose
- 4 GB RAM minimum
- Connexion Internet

## 🚀 Installation et Démarrage Rapide

### 1. Cloner le repository

```bash
git clone <your-repo-url>
cd API
```

### 2. Configuration

Copier le fichier d'exemple et éditer les variables :

```bash
cp .env.example .env
nano .env
```

**Variables importantes à modifier :**

```env
# Sécurité (OBLIGATOIRE EN PRODUCTION)
SECRET_KEY=votre-clé-secrète-très-longue-et-complexe
API_KEY=votre-clé-api-personnalisée

# Base de données
POSTGRES_PASSWORD=changez-ce-mot-de-passe

# Email verification
EMAIL_VERIFICATION_FROM=verify@votre-domaine.com
```

### 3. Démarrage avec Docker

```bash
# Lancer tous les services
docker-compose up -d

# Vérifier que tout fonctionne
docker-compose ps
```

Les services suivants démarrent :
- **API** : http://localhost:8000
- **PostgreSQL** : localhost:5432
- **Redis** : localhost:6379
- **Celery Worker** : Traitement des jobs
- **Celery Beat** : Tâches planifiées
- **Flower** : Monitoring Celery sur http://localhost:5555

### 4. Initialisation de la base de données

```bash
# Entrer dans le conteneur API
docker-compose exec api bash

# Initialiser la base de données
python -m app.utils.init_db

# Sortir du conteneur
exit
```

### 5. Vérification

```bash
# Test de santé
curl http://localhost:8000/health

# Documentation interactive
open http://localhost:8000/docs
```

## 📖 Documentation API

### Accès à la documentation

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

### Authentification

Toutes les requêtes nécessitent l'en-tête :

```
X-API-Key: votre-clé-api
```

### Endpoints Principaux

#### 1. Créer une recherche de leads

```bash
POST /api/v1/search_jobs
```

**Exemple de requête :**

```bash
curl -X POST "http://localhost:8000/api/v1/search_jobs" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "plomberie",
    "function": "gérant",
    "location": {
      "lat": 48.8566,
      "lng": 2.3522
    },
    "radius_km": 20,
    "max_results": 200
  }'
```

**Réponse :**

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "estimated_time": "400s"
}
```

#### 2. Vérifier le statut d'un job

```bash
GET /api/v1/scrapes/{job_id}
```

**Exemple :**

```bash
curl "http://localhost:8000/api/v1/scrapes/123e4567-e89b-12d3-a456-426614174000" \
  -H "X-API-Key: your-api-key-here"
```

**Réponse :**

```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "started_at": "2023-10-01T10:00:00Z",
  "completed_at": "2023-10-01T10:15:00Z",
  "sources_used": ["PagesJaunes.fr", "Kompass.com"],
  "total_found": 250,
  "total_saved": 180
}
```

#### 3. Récupérer les leads

```bash
GET /api/v1/leads/{job_id}
```

**Exemple :**

```bash
curl "http://localhost:8000/api/v1/leads/123e4567-e89b-12d3-a456-426614174000?page=1&page_size=50" \
  -H "X-API-Key: your-api-key-here"
```

**Réponse :**

```json
{
  "leads": [
    {
      "id": "uuid",
      "first_name": "Jean",
      "last_name": "Dupont",
      "function": "Gérant",
      "email": "jean.dupont@plomberie-paris.fr",
      "company": "Plomberie Paris Services",
      "address": "123 Rue de Rivoli, 75001 Paris",
      "phone": "+33123456789",
      "website": "https://plomberie-paris.fr",
      "sector": "plomberie",
      "location_distance_km": 5.2,
      "email_verified": true,
      "confidence_score": 0.85,
      "tags": ["verified_email"],
      "source": "PagesJaunes.fr",
      "scraped_at": "2023-10-01T10:00:00Z"
    }
  ],
  "total": 180,
  "filtered": 50,
  "page": 1,
  "page_size": 50
}
```

#### 4. Exporter les leads

```bash
GET /api/v1/leads/{job_id}/export?format=csv
```

**Exemple :**

```bash
# Export CSV
curl "http://localhost:8000/api/v1/leads/123e4567-e89b-12d3-a456-426614174000/export?format=csv" \
  -H "X-API-Key: your-api-key-here" \
  -o leads.csv

# Export JSON
curl "http://localhost:8000/api/v1/leads/123e4567-e89b-12d3-a456-426614174000/export?format=json" \
  -H "X-API-Key: your-api-key-here" \
  -o leads.json
```

#### 5. Gestion des consentements (RGPD)

**Opt-out (révocation du consentement) :**

```bash
POST /api/v1/consents/revoke
```

```bash
curl -X POST "http://localhost:8000/api/v1/consents/revoke" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "contact@example.com",
    "request_type": "opt_out",
    "reason": "Ne souhaite plus recevoir de sollicitations"
  }'
```

**Suppression complète des données :**

```bash
POST /api/v1/consents/delete
```

## 🧪 Tests

### Lancer les tests

```bash
# Tous les tests
docker-compose exec api pytest

# Tests avec couverture
docker-compose exec api pytest --cov=app --cov-report=html

# Tests spécifiques
docker-compose exec api pytest tests/test_api_endpoints.py
```

## 🛠️ Architecture Technique

### Stack
- **Backend** : FastAPI (Python 3.11)
- **Database** : PostgreSQL 15 + PostGIS
- **Cache/Queue** : Redis 7
- **Task Queue** : Celery
- **Scraping** : BeautifulSoup4 + Requests + Playwright
- **Email Verification** : dnspython + smtplib

### Structure du Projet

```
API/
├── app/
│   ├── api/v1/              # Endpoints API
│   │   └── endpoints/
│   │       ├── search.py
│   │       ├── scrapes.py
│   │       ├── leads.py
│   │       └── consents.py
│   ├── models/              # Modèles SQLAlchemy
│   ├── schemas/             # Schémas Pydantic
│   ├── services/            # Logique métier
│   │   ├── auth.py
│   │   └── email_verifier.py
│   ├── workers/             # Workers Celery
│   │   ├── scraper/
│   │   │   ├── spiders/
│   │   │   │   ├── pagesjaunes_spider.py
│   │   │   │   ├── kompass_spider.py
│   │   │   │   └── societe_spider.py
│   │   │   └── orchestrator.py
│   │   └── tasks.py
│   ├── config.py            # Configuration
│   ├── database.py          # Configuration DB
│   └── main.py              # Application FastAPI
├── tests/                   # Tests
├── alembic/                 # Migrations
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔧 Configuration Avancée

### Variables d'Environnement

Voir `.env.example` pour la liste complète.

**Paramètres de scraping :**

```env
USER_AGENT=LeadGenBot/1.0 (+https://yourapi.com/bot)
CONCURRENT_REQUESTS=2
DOWNLOAD_DELAY=2
RESPECT_ROBOTS_TXT=True
```

**Limites de taux :**

```env
RATE_LIMIT_PER_DAY=1000
RATE_LIMIT_PER_HOUR=100
```

### Monitoring

Accédez à Flower pour surveiller les tâches Celery :

```
http://localhost:5555
```

## 📊 Exemple Complet : Recherche Plombiers Paris

### 1. Créer la recherche

```bash
curl -X POST "http://localhost:8000/api/v1/search_jobs" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "plomberie",
    "function": "gérant",
    "location": {"lat": 48.8566, "lng": 2.3522},
    "radius_km": 20,
    "max_results": 200
  }'
```

### 2. Attendre la complétion

```bash
# Vérifier le statut toutes les 30 secondes
watch -n 30 'curl -s "http://localhost:8000/api/v1/scrapes/{job_id}" -H "X-API-Key: your-api-key-here" | jq .status'
```

### 3. Récupérer les résultats

```bash
# Voir les leads
curl "http://localhost:8000/api/v1/leads/{job_id}" \
  -H "X-API-Key: your-api-key-here" | jq .

# Exporter en CSV
curl "http://localhost:8000/api/v1/leads/{job_id}/export?format=csv" \
  -H "X-API-Key: your-api-key-here" \
  -o plombiers_paris.csv
```

## 🔐 Sécurité & Production

### Checklist avant mise en production

- [ ] Changer `SECRET_KEY` (utiliser une clé aléatoire de 64+ caractères)
- [ ] Changer `API_KEY` (utiliser une clé forte)
- [ ] Changer `POSTGRES_PASSWORD`
- [ ] Configurer `DEBUG=False`
- [ ] Configurer CORS correctement (pas `allow_origins=["*"]`)
- [ ] Mettre en place HTTPS (reverse proxy nginx/traefik)
- [ ] Configurer des sauvegardes PostgreSQL
- [ ] Mettre en place un monitoring (Prometheus/Grafana)
- [ ] Configurer des alertes

### Sécurité des données

- Chiffrement : Les données sensibles sont stockées avec chiffrement
- Logs d'audit : Toutes les actions sont tracées
- Suppression automatique : Données > 3 ans supprimées automatiquement
- Anonymisation : Option pour anonymiser les données au lieu de les supprimer

## 📝 RGPD - Politique de Confidentialité

### Finalité
Prospection commerciale B2B légale.

### Base légale
Intérêt légitime (Art. 6.1.f RGPD).

### Données collectées
- Identité professionnelle : nom, prénom, fonction
- Contact professionnel : email, téléphone
- Entreprise : nom, adresse, secteur

### Durée de conservation
3 ans maximum. Suppression automatique au-delà.

### Droits des personnes
- Droit d'accès
- Droit de rectification
- Droit à l'effacement
- Droit d'opposition (opt-out)

**Contact pour exercer vos droits** : Via l'endpoint `/api/v1/consents/revoke`

## 🐛 Dépannage

### Le service ne démarre pas

```bash
# Vérifier les logs
docker-compose logs api
docker-compose logs db

# Redémarrer les services
docker-compose restart
```

### Les jobs restent en "queued"

```bash
# Vérifier que Celery fonctionne
docker-compose logs celery_worker

# Redémarrer Celery
docker-compose restart celery_worker
```

### Problème de connexion à la DB

```bash
# Vérifier que PostgreSQL est démarré
docker-compose ps db

# Se connecter manuellement
docker-compose exec db psql -U leadgen -d leadgen_db
```

## 🤝 Contributing

Les contributions sont les bienvenues ! Merci de :

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 License

Ce projet est sous licence MIT. Voir `LICENSE` pour plus de détails.

## ⚖️ Disclaimer

Cet outil est fourni à des fins éducatives et de prospection B2B légale uniquement.

**L'utilisateur est entièrement responsable de :**
- La conformité légale de son usage
- Le respect des TOS des sites scrapés
- La conformité RGPD
- L'usage éthique des données collectées

**L'auteur décline toute responsabilité** en cas d'usage illégal ou non éthique.

---

**Développé avec ❤️ pour la prospection B2B légale et éthique**
