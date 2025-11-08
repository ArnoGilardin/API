# Contributing to B2B Lead Generation API

Merci de votre intérêt pour contribuer à ce projet ! 🎉

## Code of Conduct

Ce projet adhère à un code de conduite. En participant, vous vous engagez à respecter ce code.

**Principes :**
- Respect et bienveillance
- Collaboration constructive
- Focus sur la qualité et la légalité
- **Éthique avant tout** : Pas de contributions facilitant des usages illégaux

## Comment Contribuer

### 🐛 Signaler un Bug

1. Vérifier que le bug n'est pas déjà signalé dans les [Issues](../../issues)
2. Créer une nouvelle issue avec le template "Bug Report"
3. Fournir :
   - Description claire du problème
   - Steps to reproduce
   - Comportement attendu vs obtenu
   - Environnement (OS, Python version, Docker version)
   - Logs pertinents

### ✨ Proposer une Feature

1. Créer une issue avec le template "Feature Request"
2. Décrire :
   - Le problème que la feature résout
   - La solution proposée
   - Les alternatives considérées
   - **Implications légales** (si applicable)

### 🔧 Soumettre un Pull Request

#### 1. Fork & Clone

```bash
git clone https://github.com/votre-username/API.git
cd API
git checkout -b feature/ma-super-feature
```

#### 2. Setup Development Environment

```bash
# Copier .env
cp .env.example .env

# Lancer avec Docker
docker-compose up -d

# Installer pre-commit hooks (optionnel)
pip install pre-commit
pre-commit install
```

#### 3. Développer

- Suivre le style de code existant (PEP 8)
- Ajouter des tests pour toute nouvelle fonctionnalité
- Mettre à jour la documentation si nécessaire
- Commenter le code (surtout parties complexes)

#### 4. Tester

```bash
# Lancer les tests
make test

# Vérifier la couverture
make test-coverage

# Tests spécifiques
docker-compose exec api pytest tests/test_api_endpoints.py -v
```

#### 5. Commit

Utiliser des messages de commit clairs :

```
feat: Add email validation for disposable domains
fix: Correct SMTP timeout handling
docs: Update README with new endpoint
test: Add tests for consent revocation
refactor: Simplify spider base class
```

**Format :**
```
<type>: <description>

[optional body]

[optional footer]
```

**Types :**
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Documentation
- `test`: Tests
- `refactor`: Refactoring
- `perf`: Amélioration de performance
- `chore`: Tâches diverses (dependencies, etc.)

#### 6. Push & PR

```bash
git push origin feature/ma-super-feature
```

Créer une Pull Request sur GitHub avec :
- Description claire des changements
- Lien vers l'issue associée (si applicable)
- Screenshots (si UI/output visible)
- Checklist complétée

## Checklist PR

Avant de soumettre votre PR, vérifier :

- [ ] Le code suit PEP 8
- [ ] Tous les tests passent
- [ ] Nouveaux tests ajoutés (si feature)
- [ ] Documentation mise à jour
- [ ] Pas de code mort ou de debug logs
- [ ] Pas de secrets/credentials hardcodés
- [ ] Implications RGPD vérifiées (si applicable)
- [ ] Aspects légaux vérifiés (si scraping)

## Standards de Code

### Python Style

- Suivre **PEP 8**
- Utiliser **type hints** quand possible
- Docstrings pour toutes les fonctions publiques
- Longueur de ligne max : 100 caractères

**Exemple :**

```python
def verify_email(email: str, timeout: int = 10) -> bool:
    """
    Verify if an email address is valid and deliverable.

    Args:
        email: Email address to verify
        timeout: SMTP timeout in seconds

    Returns:
        True if email is valid, False otherwise

    Raises:
        ValueError: If email format is invalid
    """
    # Implementation
    pass
```

### Tests

- **Pytest** pour tous les tests
- Couverture minimale : **80%**
- Tests unitaires ET tests d'intégration
- Utiliser fixtures quand possible

**Exemple :**

```python
def test_email_verification_valid(mocker):
    """Test email verification with valid email."""
    # Arrange
    mocker.patch('dns.resolver.resolve', return_value=[...])

    # Act
    result = verify_email("valid@example.com")

    # Assert
    assert result is True
```

### Documentation

- Markdown pour docs
- Docstrings Python (Google style)
- Exemples de code fonctionnels
- Mise à jour du README si nécessaire

## Aspects Légaux

### ⚠️ Règles Strictes

Toute contribution doit respecter :

1. **Pas de LinkedIn scraping**
   - Aucun code facilitant le scraping de LinkedIn
   - PRs avec du code LinkedIn seront **rejetées immédiatement**

2. **Respect de robots.txt**
   - Toujours vérifier robots.txt avant scraping
   - Implémenter rate limiting approprié

3. **RGPD Compliance**
   - Minimisation des données
   - Consentement et opt-out
   - Sécurité des données

4. **Données publiques uniquement**
   - Pas de scraping de données privées
   - Sources publiques professionnelles uniquement

### Revue Légale

Les PRs touchant au scraping ou RGPD seront **revues attentivement** :
- Vérification de la légalité
- Impact sur la conformité RGPD
- Risques potentiels

## Architecture

### Structure du Code

```
app/
├── api/v1/              # Endpoints API
├── models/              # Modèles DB (SQLAlchemy)
├── schemas/             # Validation (Pydantic)
├── services/            # Logique métier
├── workers/             # Celery tasks
│   └── scraper/
│       └── spiders/     # Spiders de scraping
└── utils/               # Utilitaires
```

### Bonnes Pratiques

1. **Separation of Concerns**
   - API endpoints = routing + validation
   - Services = business logic
   - Models = data structure

2. **Dependency Injection**
   - Utiliser FastAPI dependencies
   - Facilite les tests (mocking)

3. **Error Handling**
   - Exceptions spécifiques
   - Messages d'erreur clairs
   - Logging approprié

4. **Async When Possible**
   - Utiliser async/await pour I/O
   - Celery pour long-running tasks

## Nouvelles Fonctionnalités

### Ideas Bienvenues

- 🔍 Nouveaux scrapers (si légaux)
- 📊 Amélioration du scoring
- 🌍 Enrichissement géographique
- 📧 Amélioration de l'email verification
- 🔒 Renforcement de la sécurité
- 📈 Monitoring et métriques
- 🧪 Plus de tests

### Processus

1. Créer une issue pour discussion
2. Attendre feedback des maintainers
3. Développer sur une branche
4. Soumettre PR avec tests
5. Review et merge

## Questions ?

N'hésitez pas à :
- Ouvrir une [Discussion](../../discussions)
- Poser une question dans les [Issues](../../issues)
- Contacter les maintainers

## Remerciements

Merci à tous les contributeurs qui rendent ce projet meilleur ! 🙏

Votre contribution, quelle qu'elle soit (code, docs, bugs reports), est précieuse.

---

**Happy Coding! 🚀**
