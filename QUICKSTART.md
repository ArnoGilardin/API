# 🚀 Quick Start Guide - B2B Lead Generation API

Guide de démarrage rapide en 5 minutes.

## Prérequis

- Docker & Docker Compose installés
- 4 GB RAM minimum
- Port 8000, 5432, 6379, 5555 disponibles

## Installation en 3 Étapes

### 1️⃣ Configuration

```bash
# Copier et éditer le fichier .env
cp .env.example .env

# Éditer (optionnel pour le dev)
nano .env
```

### 2️⃣ Démarrage

```bash
# Lancer tous les services
docker-compose up -d

# Vérifier que tout tourne
docker-compose ps
```

**Attendez 30 secondes** que PostgreSQL soit prêt.

### 3️⃣ Initialisation

```bash
# Initialiser la base de données
docker-compose exec api python -m app.utils.init_db
```

## ✅ Vérification

### Test de santé

```bash
curl http://localhost:8000/health
```

**Réponse attendue :**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development"
}
```

### Documentation

Ouvrez dans votre navigateur : http://localhost:8000/docs

## 🎯 Premier Test

### 1. Créer une recherche

```bash
curl -X POST "http://localhost:8000/api/v1/search_jobs" \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "plomberie",
    "function": "gérant",
    "location": {
      "lat": 48.8566,
      "lng": 2.3522
    },
    "radius_km": 20,
    "max_results": 50
  }'
```

**Sauvegardez le `job_id` retourné !**

### 2. Vérifier le statut

```bash
# Remplacez {JOB_ID} par votre job_id
curl "http://localhost:8000/api/v1/scrapes/{JOB_ID}" \
  -H "X-API-Key: dev-api-key-12345"
```

### 3. Récupérer les leads (quand status = "completed")

```bash
curl "http://localhost:8000/api/v1/leads/{JOB_ID}" \
  -H "X-API-Key: dev-api-key-12345"
```

## 🔧 Commandes Utiles

### Docker Compose

```bash
# Voir les logs
docker-compose logs -f api

# Redémarrer un service
docker-compose restart api

# Arrêter tout
docker-compose down

# Arrêter ET supprimer les volumes (⚠️ supprime la DB)
docker-compose down -v
```

### Makefile (raccourcis)

```bash
make up          # Démarrer
make down        # Arrêter
make logs        # Voir les logs
make test        # Lancer les tests
make shell       # Ouvrir un shell dans le conteneur
make init-db     # Initialiser la DB
```

## 📊 Interfaces Web

- **API Docs (Swagger)** : http://localhost:8000/docs
- **API Docs (ReDoc)** : http://localhost:8000/redoc
- **Flower (Celery)** : http://localhost:5555

## 🐛 Dépannage

### Services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Reconstruire
docker-compose build --no-cache
docker-compose up -d
```

### Port déjà utilisé

```bash
# Modifier dans docker-compose.yml
# Exemple : changer "8000:8000" en "8080:8000"
```

### Base de données corrompue

```bash
# ATTENTION : Supprime toutes les données
docker-compose down -v
docker-compose up -d
docker-compose exec api python -m app.utils.init_db
```

### Job reste en "queued"

```bash
# Vérifier que Celery tourne
docker-compose ps celery_worker

# Voir les logs Celery
docker-compose logs celery_worker

# Redémarrer Celery
docker-compose restart celery_worker
```

## 🧪 Tests

```bash
# Tous les tests
make test

# Test spécifique
docker-compose exec api pytest tests/test_api_endpoints.py -v

# Avec couverture
make test-coverage
```

## 📚 Prochaines Étapes

1. **Lire le README complet** : [README.md](README.md)
2. **Comprendre l'architecture** : [ARCHITECTURE.md](ARCHITECTURE.md)
3. **Voir la politique RGPD** : [PRIVACY_POLICY.md](PRIVACY_POLICY.md)
4. **Contribuer** : [CONTRIBUTING.md](CONTRIBUTING.md)

## 🔐 Sécurité (Production)

⚠️ **Avant de déployer en production :**

1. Changer `SECRET_KEY` dans `.env`
2. Changer `API_KEY` dans `.env`
3. Changer `POSTGRES_PASSWORD` dans `.env`
4. Mettre `DEBUG=False`
5. Configurer HTTPS (nginx/traefik)
6. Configurer des backups

Voir [README.md](README.md) section "Sécurité & Production".

## 💡 Exemples d'Utilisation

### Recherche de plombiers à Paris

```bash
curl -X POST "http://localhost:8000/api/v1/search_jobs" \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "plomberie",
    "location": {"lat": 48.8566, "lng": 2.3522},
    "radius_km": 15,
    "max_results": 100
  }'
```

### Recherche de directeurs commerciaux dans le BTP

```bash
curl -X POST "http://localhost:8000/api/v1/search_jobs" \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "btp",
    "function": "directeur commercial",
    "max_results": 200
  }'
```

### Export CSV

```bash
curl "http://localhost:8000/api/v1/leads/{JOB_ID}/export?format=csv" \
  -H "X-API-Key: dev-api-key-12345" \
  -o leads.csv
```

### Opt-out RGPD

```bash
curl -X POST "http://localhost:8000/api/v1/consents/revoke" \
  -H "X-API-Key: dev-api-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "contact@example.com",
    "request_type": "opt_out"
  }'
```

## 📞 Support

**Problème ?**
- Consulter la section Dépannage ci-dessus
- Voir les [Issues](../../issues) existantes
- Créer une nouvelle issue

**Question ?**
- Consulter la [Documentation](http://localhost:8000/docs)
- Lire le [README](README.md)
- Ouvrir une [Discussion](../../discussions)

---

**Bon scraping ! 🚀** (légal et éthique, bien sûr 😉)
