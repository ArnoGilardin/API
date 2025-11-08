# Architecture Technique - B2B Lead Generation API

## Vue d'Ensemble

```
┌─────────────┐
│   Client    │
│ (Browser/   │
│  CLI/CRM)   │
└──────┬──────┘
       │ HTTP/REST
       │
┌──────▼──────────────────────────────────────┐
│          FastAPI Application                │
│  ┌────────────────────────────────────┐     │
│  │   API Endpoints (v1)               │     │
│  │  - /search_jobs                    │     │
│  │  - /scrapes/{id}                   │     │
│  │  - /leads/{id}                     │     │
│  │  - /consents/revoke                │     │
│  └────────┬───────────────────────────┘     │
│           │                                  │
│  ┌────────▼───────────┐  ┌────────────────┐ │
│  │  Authentication    │  │   Validation   │ │
│  │  (API Key/JWT)     │  │   (Pydantic)   │ │
│  └────────────────────┘  └────────────────┘ │
└──────┬────────────────────┬──────────────────┘
       │                    │
       │ SQLAlchemy         │ Celery Tasks
       │                    │
┌──────▼────────┐    ┌──────▼────────────────┐
│  PostgreSQL   │    │   Redis (Broker)      │
│  + PostGIS    │    └──────┬────────────────┘
│               │           │
│ Tables:       │           │
│ - leads       │    ┌──────▼────────────────┐
│ - companies   │    │  Celery Workers       │
│ - sources     │    │                       │
│ - scrapes     │    │ ┌──────────────────┐  │
│ - consents    │    │ │ Scraping Jobs    │  │
│ - enrichments │    │ │                  │  │
│ - logs        │    │ │ - PagesJaunes    │  │
└───────────────┘    │ │ - Kompass        │  │
                     │ │ - Societe.com    │  │
                     │ └──────────────────┘  │
                     │                       │
                     │ ┌──────────────────┐  │
                     │ │ Email Verify     │  │
                     │ │ - DNS MX         │  │
                     │ │ - SMTP Check     │  │
                     │ └──────────────────┘  │
                     └───────────────────────┘
```

## Composants Principaux

### 1. FastAPI Application (app/main.py)

**Responsabilités :**
- Exposition des endpoints REST
- Validation des requêtes (Pydantic)
- Authentification et autorisation
- Gestion des erreurs
- Documentation OpenAPI

**Technologies :**
- FastAPI 0.109+
- Pydantic pour validation
- SQLAlchemy pour ORM
- JWT/API Key pour auth

### 2. Database Layer (PostgreSQL + PostGIS)

**Schéma :**
- `sources` : Sources de données (PagesJaunes, etc.)
- `companies` : Entreprises
- `leads` : Leads avec géolocalisation
- `scrapes` : Jobs de scraping
- `enrichments` : Données enrichies
- `consents` : Consentements RGPD
- `logs` : Audit trail

**Extensions :**
- PostGIS pour requêtes géographiques
- UUID pour identifiants
- JSONB pour données flexibles
- GIN/GIST indexes pour performance

### 3. Task Queue (Celery + Redis)

**Workers :**
- `celery_worker` : Traitement des tâches
- `celery_beat` : Tâches planifiées

**Tâches :**
- `start_scraping_job` : Lance le scraping
- `verify_lead_email` : Vérifie les emails
- `cleanup_old_data` : Nettoyage RGPD (quotidien)

### 4. Scraping Engine

**Architecture modulaire :**

```python
BaseSpider (abstract)
    ├── PagesJaunesSpider
    ├── KompassSpider
    └── SocieteSpider
```

**Fonctionnalités communes :**
- Respect de robots.txt
- Rate limiting
- Extraction d'emails (regex)
- Extraction de téléphones
- Calcul de score de confiance

### 5. Email Verification Service

**Pipeline :**
1. Format validation
2. DNS MX record check
3. SMTP connection test
4. Deliverability check

**Mise à jour automatique :**
- Tag `verified_email` si valide
- Tag `invalid_email` si invalide
- Ajustement du `confidence_score`

## Flux de Données

### Création d'un Job de Scraping

```
1. Client → POST /api/v1/search_jobs
   {
     "sector": "plomberie",
     "location": {"lat": 48.85, "lng": 2.35},
     "radius_km": 20
   }

2. API → Validation (Pydantic)
   - Vérification des paramètres
   - Vérification de l'authentification

3. API → Create Scrape record (PostgreSQL)
   - job_id généré
   - status = "queued"

4. API → Queue task (Celery)
   start_scraping_job.delay(job_id, params)

5. API → Response
   {
     "job_id": "uuid",
     "status": "queued",
     "estimated_time": "300s"
   }

6. Worker → Execute task
   - Update status = "running"
   - Scrape PagesJaunes, Kompass, Societe.com
   - Save leads to DB
   - Update status = "completed"

7. Worker → Queue email verification
   For each lead:
     verify_lead_email.delay(lead_id)

8. Client → GET /api/v1/scrapes/{job_id}
   Monitor progress

9. Client → GET /api/v1/leads/{job_id}
   Retrieve results
```

## Sécurité

### Authentification

**API Key (Header) :**
```
X-API-Key: your-api-key-here
```

**Validation :**
- Middleware vérifie la clé sur chaque requête
- Rate limiting par clé API
- Logs d'audit pour toutes les actions

### Protection des Données

**Chiffrement :**
- Connexions HTTPS (en production)
- Données sensibles chiffrées en DB (AES-256)

**Accès :**
- Principe du moindre privilège
- Isolation des services (Docker networks)
- Pas d'exposition directe de la DB

## Performance

### Optimisations

**Database :**
- Indexes sur colonnes fréquemment requêtées
- PostGIS GIST index pour géolocalisation
- Connection pooling (SQLAlchemy)

**Caching :**
- Redis pour résultats de jobs
- Cache robots.txt (15 min)

**Async Processing :**
- Jobs de scraping asynchrones (Celery)
- Vérification d'emails en parallèle
- Pagination pour grands datasets

### Scalabilité

**Horizontal Scaling :**
- Workers Celery scalables indépendamment
- API stateless (peut être répliquée)
- PostgreSQL peut être shardé par région

**Vertical Scaling :**
- DB peut être upgradée (plus de CPU/RAM)
- Workers peuvent avoir plus de concurrency

## Monitoring

### Métriques

**Application :**
- Request rate
- Response time
- Error rate
- Success rate par endpoint

**Celery :**
- Task queue length
- Task processing time
- Worker status
- Failed tasks

**Database :**
- Connection count
- Query time
- Slow queries
- Disk usage

### Outils

- **Flower** : Monitoring Celery (http://localhost:5555)
- **PostgreSQL logs** : Query performance
- **Application logs** : Erreurs et events

## RGPD Compliance

### Principes Implémentés

1. **Minimisation des données**
   - Collecte uniquement des données nécessaires
   - Pas de données sensibles

2. **Limitation de la conservation**
   - Auto-suppression après 3 ans
   - Tâche quotidienne `cleanup_old_data`

3. **Droits des personnes**
   - Opt-out via `/consents/revoke`
   - Suppression via `/consents/delete`
   - Audit trail complet

4. **Sécurité**
   - Chiffrement
   - Authentification
   - Logs d'accès

## Déploiement Production

### Checklist

- [ ] Environnement `.env` sécurisé
- [ ] HTTPS activé (reverse proxy)
- [ ] Backups PostgreSQL (quotidiens)
- [ ] Monitoring actif
- [ ] Rate limiting configuré
- [ ] Logs centralisés
- [ ] Alertes configurées

### Recommandations Infrastructure

**Minimum :**
- 2 vCPU
- 4 GB RAM
- 50 GB SSD

**Recommandé :**
- 4 vCPU
- 8 GB RAM
- 100 GB SSD
- Load balancer (si > 1 instance API)

## Maintenance

### Tâches Régulières

**Quotidien :**
- Vérifier logs d'erreurs
- Monitorer performance Celery
- Vérifier espace disque

**Hebdomadaire :**
- Backup manuel de vérification
- Review des failed tasks
- Mise à jour des dépendances (si nécessaire)

**Mensuel :**
- Audit RGPD (consentements, suppressions)
- Revue des métriques de qualité (email verification rate)
- Nettoyage des logs anciens

## Support & Troubleshooting

### Problèmes Courants

**Job reste en "queued" :**
- Vérifier que Celery worker tourne
- Vérifier Redis connectivity
- Check Celery logs

**Pas de leads trouvés :**
- Vérifier robots.txt des sources
- Vérifier connectivité réseau
- Logs du spider

**Emails non vérifiés :**
- Vérifier `SMTP_VERIFY_ENABLED=True`
- Vérifier connectivité SMTP
- Timeout trop court ?

### Logs Importants

```bash
# API logs
docker-compose logs api

# Celery worker logs
docker-compose logs celery_worker

# PostgreSQL logs
docker-compose logs db
```
