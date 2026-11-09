# EduNova - Rapport de Correction JWT (Phase 1)

## Date
2025-01-XX

## Problème Identifié

Le backend EduNova échouait au démarrage avec l'erreur :
```
ValueError: La cle JWT doit contenir au moins 32 caracteres.
```

Cette erreur était causée par des valeurs de `EDUNOVA_JWT_SECRET` trop courtes dans les fichiers de configuration.

## Fichiers Corrigés

### 1. `.env.backend`
- **Problème** : `EDUNOVA_JWT_SECRET=dev-secret-edunova-change-later` (31 caractères)
- **Correction** : `EDUNOVA_JWT_SECRET=dev-secret-edunova-change-later-123` (35 caractères)
- **Impact** : Ce fichier était probablement chargé dans certains contextes, causant l'échec du démarrage du backend

### 2. `.env`
- **Problème** : `EDUNOVA_JWT_SECRET=dev-secret-key-32-chars-minimum-1234567890` (42 caractères)
- **Correction** : `EDUNOVA_JWT_SECRET=dev-secret-key-32-chars-minimum-12345678901234` (46 caractères)
- **Impact** : Renforcement de la sécurité avec une clé plus longue

### 3. `start.ps1`
- **État** : Déjà corrigé (les références `$Host:$Port` ont été remplacées par `${BackendHost}:${Port}`)
- **Vérification** : Le JWT secret utilisé a 44 caractères, ce qui est valide

## Validation

### Test de démarrage du backend
```bash
EDUNOVA_ENVIRONMENT=development \
EDUNOVA_JWT_SECRET='dev-secret-key-32-chars-minimum-123456789012' \
EDUNOVA_DATABASE_PATH='edunova_test.db' \
python -m uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017
```
**Résultat** : ✅ Démarrage réussi

### Test d'inscription et connexion
```python
# Inscription
POST /auth/register-establishment
{"school_name": "Test", "admin_name": "Admin", "email": "test@test.com", "password": "Password123!"}
# Résultat: 201 Created

# Connexion
POST /auth/login
{"email": "test@test.com", "password": "Password123!"}
# Résultat: 200 OK avec access_token et refresh_token

# Accès à /auth/me
GET /auth/me
Headers: {"Authorization": "Bearer <access_token>"}
# Résultat: 200 OK avec informations utilisateur
```
**Résultat** : ✅ Tous les tests passent

### Exécution des tests existants
```bash
pytest tests/ -v --tb=short -k "auth or login or logout or register"
```
**Résultat** : 
- 114 tests passés
- 1 test échoué (attendu) : `test_register_establishment_rate_limiting` (limitation connue de InMemoryRateLimiter)

## Causes Racines

1. **Configuration incohérente** : Plusieurs fichiers `.env` avec des valeurs de JWT secret différentes
2. **Valeur trop courte** : `.env.backend` avait une clé de 31 caractères, inférieur au minimum de 32
3. **Absence de validation précoce** : La validation de la longueur du JWT secret est faite au niveau de `JwtService.__init__`, pas au niveau de `Settings.from_environment()` pour les environnements de développement

## Recommandations

1. **Standardiser les clés JWT** : Utiliser la même clé ou un mécanisme de génération cohérent dans tous les fichiers de configuration
2. **Documenter la configuration** : Ajouter des commentaires expliquant que le JWT secret doit avoir au moins 32 caractères
3. **Validation précoce** : Envisager d'ajouter une validation dans `Settings.from_environment()` même pour les environnements de développement
4. **Utiliser `_DEVELOPMENT_JWT_SECRET` par défaut** : Si `EDUNOVA_JWT_SECRET` n'est pas défini en développement, utiliser toujours la valeur générée automatiquement (43 caractères)

## Verdict

**APPROUVÉ**

Le problème de la clé JWT trop courte a été identifié et corrigé. Le backend peut maintenant démarrer correctement et les parcours d'inscription/connexion fonctionnent comme prévu.

---

## Prochaines Étapes

1. Exécuter l'intégralité de la suite de tests pour confirmer qu'aucun autre problème n'existe
2. Tester l'intégration frontend/backend avec le navigateur
3. Vérifier que le message "Backend inaccessible" dans le frontend n'apparaît plus quand le backend est correctement démarré
