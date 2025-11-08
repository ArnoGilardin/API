# Politique de Confidentialité - B2B Lead Generation API

**Dernière mise à jour : Novembre 2024**

## 1. Responsable du Traitement

**Nom de l'organisation** : [Votre Entreprise]
**Email de contact** : contact@votre-entreprise.com
**Adresse** : [Votre adresse]

## 2. Finalité du Traitement

Cette API collecte et traite des données professionnelles publiques dans le but de :
- Génération de leads B2B
- Prospection commerciale légale
- Constitution de bases de données professionnelles

## 3. Base Légale

Le traitement repose sur **l'intérêt légitime** (Article 6.1.f du RGPD) :
- Les données collectées sont publiques et professionnelles
- La finalité est la prospection B2B légale
- Les droits des personnes sont respectés (opposition, accès, effacement)

## 4. Données Collectées

### 4.1 Catégories de Données

Nous collectons **uniquement des données professionnelles publiques** :

**Identité professionnelle :**
- Nom et prénom
- Fonction/Titre professionnel

**Contact professionnel :**
- Adresse email professionnelle
- Numéro de téléphone professionnel

**Entreprise :**
- Nom de l'entreprise
- Adresse du siège social
- Site web
- Secteur d'activité
- SIREN/SIRET (données légales publiques)

### 4.2 Sources de Données

Données collectées depuis des **sources publiques uniquement** :
- Annuaires professionnels (PagesJaunes.fr)
- Bases de données B2B (Kompass.com)
- Données légales publiques (Societe.com, Pappers.fr)
- Sites web d'entreprises (pages "Équipe" ou "Contact")

**Sources EXCLUES :**
- ❌ LinkedIn (interdit par TOS)
- ❌ Réseaux sociaux personnels
- ❌ Bases de données privées non autorisées

## 5. Minimisation des Données

Conformément au principe de minimisation du RGPD :
- Seules les données nécessaires à la prospection B2B sont collectées
- Pas de données sensibles (origine, religion, santé, etc.)
- Pas de données personnelles privées (adresse domicile, téléphone perso)

## 6. Durée de Conservation

**Conservation maximale : 3 ans**

Après cette période :
- Suppression automatique des données
- Système de nettoyage quotidien (`cleanup_old_data`)
- Logs conservés pour audit (1 an maximum)

## 7. Destinataires des Données

Les données sont accessibles à :
- L'utilisateur de l'API (détenteur de la clé API)
- Les administrateurs système (maintenance uniquement)
- Pas de transmission à des tiers sans consentement explicite

## 8. Droits des Personnes

Conformément au RGPD, vous disposez des droits suivants :

### 8.1 Droit d'Accès
Demander une copie de vos données personnelles.

### 8.2 Droit de Rectification
Corriger des données inexactes ou incomplètes.

### 8.3 Droit à l'Effacement ("Droit à l'oubli")
Demander la suppression complète de vos données.

### 8.4 Droit d'Opposition (Opt-out)
S'opposer au traitement de vos données pour prospection.

### 8.5 Droit à la Limitation
Demander la limitation du traitement dans certains cas.

## 9. Exercer vos Droits

### Via l'API

**Opt-out (opposition au traitement) :**
```bash
POST /api/v1/consents/revoke
{
  "email": "votre.email@entreprise.com",
  "request_type": "opt_out",
  "reason": "Je ne souhaite plus être contacté"
}
```

**Suppression complète des données :**
```bash
POST /api/v1/consents/delete
{
  "email": "votre.email@entreprise.com",
  "request_type": "delete",
  "reason": "Droit à l'effacement"
}
```

### Par Email

Envoyez votre demande à : **contact@votre-entreprise.com**

**Informations à fournir :**
- Nom, prénom
- Email professionnel
- Nature de la demande (accès, rectification, suppression, opposition)
- Justificatif d'identité (pour sécurité)

**Délai de réponse : Maximum 30 jours** (conformément au RGPD)

## 10. Sécurité des Données

### 10.1 Mesures Techniques

- **Chiffrement** : AES-256 pour données sensibles
- **Authentification** : API Key requise pour tout accès
- **HTTPS** : Connexions chiffrées en production
- **Isolation** : Services isolés (Docker networks)
- **Backups** : Sauvegardes chiffrées quotidiennes

### 10.2 Mesures Organisationnelles

- Accès limité aux seules personnes autorisées
- Logs d'audit pour toute action sensible
- Revue régulière des accès
- Formation RGPD des équipes

### 10.3 Incident de Sécurité

En cas de violation de données :
- Notification CNIL sous 72h
- Notification des personnes concernées si risque élevé
- Mesures correctives immédiates

## 11. Transferts Internationaux

**Pas de transfert hors UE** par défaut.

Si transfert nécessaire :
- Clauses contractuelles types (CCT)
- Garanties appropriées conformes RGPD
- Information préalable des personnes concernées

## 12. Profilage et Décisions Automatisées

### 12.1 Scoring de Qualité

Un **score de confiance** (0-1) est calculé automatiquement pour chaque lead :
- Basé sur : complétude des données, vérification email, source fiabilité
- **Pas d'impact juridique** : Score informatif uniquement
- Peut être contesté

### 12.2 Pas de Décision Automatisée à Impact Juridique

Aucune décision produisant des effets juridiques n'est prise automatiquement.

## 13. Cookies et Traceurs

L'API n'utilise **pas de cookies** pour le tracking.

Seuls cookies techniques :
- Session API (si JWT utilisé)
- Aucun cookie publicitaire ou analytics

## 14. Registre des Traitements

Un **registre des activités de traitement** est tenu conformément à l'Article 30 RGPD.

**Contenu :**
- Finalités du traitement
- Catégories de données
- Catégories de personnes concernées
- Destinataires
- Durées de conservation
- Mesures de sécurité

**Accès :** Sur demande auprès du DPO.

## 15. Délégué à la Protection des Données (DPO)

**DPO :** [Nom du DPO]
**Email :** dpo@votre-entreprise.com
**Rôle :** Point de contact pour toute question RGPD

## 16. Autorité de Contrôle

Vous avez le droit de déposer une plainte auprès de la CNIL :

**Commission Nationale de l'Informatique et des Libertés (CNIL)**
- **Adresse :** 3 Place de Fontenoy - TSA 80715 - 75334 PARIS CEDEX 07
- **Téléphone :** 01 53 73 22 22
- **Site web :** https://www.cnil.fr
- **Plainte en ligne :** https://www.cnil.fr/fr/plaintes

## 17. Modifications de la Politique

Cette politique peut être mise à jour pour refléter :
- Évolutions légales (RGPD, directives CNIL)
- Nouvelles fonctionnalités de l'API
- Amélirations de sécurité

**En cas de modification substantielle :**
- Notification par email aux utilisateurs de l'API
- Version historique disponible sur demande

## 18. Contact

Pour toute question concernant cette politique :

**Email :** contact@votre-entreprise.com
**Téléphone :** [Votre numéro]

---

**Dernière révision :** Novembre 2024
**Version :** 1.0
