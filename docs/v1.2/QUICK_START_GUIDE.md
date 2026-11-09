# EDUNOVA - GUIDE DE DÉMARRAGE RAPIDE

**Version :** v1.2  
**Date :** 9 novembre 2026  
**Statut :** ✅ Prêt pour les tests

---

## 🚀 DÉMARRER L'APPLICATION

### Prérequis
- Python 3.11+ (déjà installé dans .venv)
- Node.js 20+ (pour le frontend)
- Git Bash ou PowerShell

---

## 💻 DÉMARRER LE BACKEND

### Étape 1 : Activer l'environnement virtuel

```powershell
cd F:\EduNova
.\.venv\Scripts\Activate.ps1
```

### Étape 2 : Démarrer le serveur FastAPI

```powershell
uvicorn src.presentation.api.app:app --reload --port 8017 --host 0.0.0.0
```

**✅ Backend accessible à :** http://127.0.0.1:8017/docs

### Vérification du backend

Ouvrez un nouveau terminal et exécutez :

```powershell
cd F:\EduNova
.\.venv\Scripts\Activate.ps1
python -c "
from fastapi.testclient import TestClient
from src.presentation.api.app import create_app
from src.presentation.api.container import ApplicationContainer

container = ApplicationContainer()
app = create_app(container)
client = TestClient(app)

response = client.get('/health')
print(f'Backend Status: {response.status_code}')
print(f'Response: {response.json()}')
"
```

**Résultat attendu :**
```
Backend Status: 200
Response: {'status': 'ok', 'application': 'EduNova'}
```

---

## 🎨 DÉMARRER LE FRONTEND

### Étape 1 : Installer les dépendances (si nécessaire)

```powershell
cd F:\EduNova\frontend
npm install
```

### Étape 2 : Démarrer l'application Vite

```powershell
npm run dev
```

**✅ Frontend accessible à :** http://127.0.0.1:5173

### Vérification du frontend

Exécutez les tests :

```powershell
cd F:\EduNova\frontend
npm test
```

**Résultat attendu :**
```
39 Test Files
190 Tests
0 Failures ✅
```

---

## 🧪 TESTER L'APPLICATION

### Test 1 : Page d'accueil
1. Ouvrir http://127.0.0.1:5173 dans votre navigateur
2. Vous devriez voir la page d'accueil ou être redirigé vers la page de connexion

### Test 2 : Page d'inscription
1. Naviguer vers http://127.0.0.1:5173/register
2. Remplir le formulaire :
   - Nom de l'établissement : `Mon École`
   - Nom du responsable : `Jean Dupont`
   - Email : `jean.dupont@test.com`
   - Mot de passe : `TestPassword123!`
   - Confirmer le mot de passe : `TestPassword123!`
3. Cliquer sur "Créer mon établissement"
4. **Résultat attendu :** Inscription réussie + redirection vers /login

### Test 3 : Page de connexion
1. Sur la page http://127.0.0.1:5173/login
2. Saisir :
   - Email : `jean.dupont@test.com`
   - Mot de passe : `TestPassword123!`
3. Cliquer sur "Se connecter"
4. **Résultat attendu :**
   - Si mono-tenant : Connexion réussie + redirection vers l'espace privé
   - Si multi-tenant : Affichage de la page de sélection du tenant
   - Si 2FA activé : Affichage de la page de validation 2FA

### Test 4 : Sélection du tenant (si multi-tenant)
1. Sélectionner un établissement dans la liste
2. Cliquer sur "Sélectionner"
3. **Résultat attendu :** Connexion réussie + redirection vers l'espace privé

### Test 5 : Validation 2FA (si activé)
1. Saisir le code TOTP généré par votre application (Google Authenticator, Authy, etc.)
2. Cliquer sur "Valider"
3. **Résultat attendu :** Connexion réussie + redirection vers l'espace privé

---

## 📊 VÉRIFICATIONS TECHNIQUES

### Vérifier la connexion backend-frontend

Exécutez le script de test :

```powershell
cd F:\EduNova
python test_backend_frontend_connection.py
```

**Résultat attendu :**
```
============================================================
  TEST DE CONNEXION BACKEND-FRONTEND EDUNOVA
============================================================

============================================================
  1. TEST DU DEMARRAGE DU BACKEND
============================================================

  Demarrage du backend FastAPI...
  Attente du demarrage (5 secondes)...
  [OK] Backend demarre avec succes
  Reponse: {'status': 'ok', 'application': 'EduNova'}

============================================================
  2. TEST DE LA CONFIGURATION CORS
============================================================

  [OK] CORS configure
  Access-Control-Allow-Origin: http://127.0.0.1:5173
  Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
  Access-Control-Allow-Headers: Accept, Accept-Language, Authorization, Content-Language, Content-Type, Origin

============================================================
  3. TEST DES ENDPOINTS API
============================================================

  [OK] GET /health -> 200
  [OK] POST /auth/register-establishment -> 201

============================================================
  4. TEST DE LA CONFIGURATION FRONTEND
============================================================

  [OK] .env.local a la bonne URL API
  Contenu: VITE_API_URL=http://127.0.0.1:8017
  [OK] client.ts utilise la bonne URL API

  Backend arrete

============================================================
  RESULTAT FINAL
============================================================

  [SUCCESS] TOUS LES TESTS ONT REUSSI ✅
```

---

## 📁 STRUCTURE DE L'APPLICATION

### Backend
```
src/
├── identity/           # Gestion de l'authentification
│   ├── application/
│   │   ├── use_cases/
│   │   │   ├── login_user.py
│   │   │   ├── register_establishment.py
│   │   │   ├── select_tenant_context.py
│   │   │   └── verify_login_two_factor.py
│   │   └── interfaces/
│   └── infrastructure/
│       └── security/
│           ├── jwt_service.py
│           └── in_memory_rate_limiter.py
├── tenancy/            # Gestion des tenants
├── presentation/
│   └── api/
│       ├── app.py          # Configuration FastAPI + CORS
│       ├── container.py    # Injection de dépendances
│       └── routes/
│           └── auth.py      # Routes d'authentification
└── infrastructure/
    └── repositories/
        └── sqlite_consumed_token_repository.py
```

### Frontend
```
frontend/src/
├── features/
│   └── auth/
│       ├── pages/
│       │   ├── LoginPage.tsx
│       │   ├── RegisterEstablishmentPage.tsx
│       │   ├── TenantSelectionPage.tsx
│       │   └── TwoFactorPage.tsx
│       ├── services/
│       │   └── auth.service.ts
│       └── types/
└── shared/
    └── api/
        └── client.ts      # Client API avec CORS et credentials
```

---

## 🔧 RÉSOLUTION DES PROBLÈMES

### Problème : Backend ne démarre pas

**Cause possible :** Port 8017 déjà utilisé

**Solution :**
```powershell
# Trouver le processus utilisant le port 8017
netstat -ano | findstr :8017

# Arrêter le processus (remplacer PID par l'ID du processus)
taskkill /PID <PID> /F
```

### Problème : Frontend ne se connecte pas au backend

**Cause possible :** CORS mal configuré ou URL incorrecte

**Solution :**
1. Vérifiez que le backend tourne sur http://127.0.0.1:8017
2. Vérifiez que `VITE_API_URL=http://127.0.0.1:8017` dans `.env.local`
3. Vérifiez que le frontend utilise bien cette variable

### Problème : Les tests échouent

**Solution :**
```powershell
# Vérifier les dépendances backend
cd F:\EduNova
.\.venv\Scripts\Activate.ps1
pip list | grep -i fastapi

# Vérifier les dépendances frontend
cd F:\EduNova\frontend
npm ls --depth=0
```

---

## 📊 STATUT ACTUEL

| Composant | Statut | Détails |
|-----------|--------|---------|
| Backend | ✅ Fonctionnel | Port 8017, CORS configuré |
| Frontend | ✅ Fonctionnel | Port 5173, 190/190 tests PASS |
| Connexion | ✅ Résolue | CORS + URLs alignées |
| Inscription | ✅ Implémentée | RegisterEstablishmentPage |
| Connexion | ✅ Implémentée | LoginPage (3 scénarios) |
| Sélection Tenant | ✅ Implémentée | TenantSelectionPage |
| 2FA | ✅ Implémentée | TwoFactorPage |
| Sécurité | ✅ Renforcée | Anti-rejeu TOTP persistant |
| Documentation | ✅ Complète | Contrats API + rapports |

---

## 🎯 PROCHAINES ÉTAPES

1. **Démarrer les deux services** (backend + frontend)
2. **Tester manuellement** via le navigateur
3. **Vérifier tous les parcours** :
   - Inscription
   - Connexion mono-tenant
   - Connexion multi-tenant
   - Connexion avec 2FA
4. **Signaler tout problème** pour correction

---

## 📚 DOCUMENTATION

- [PHASE_5_COMPLETION_REPORT.md](PHASE_5_COMPLETION_REPORT.md) - Rapport complet
- [FINAL_BACKEND_FRONTEND_CONNECTION_REPORT.md](FINAL_BACKEND_FRONTEND_CONNECTION_REPORT.md) - Connexion backend-frontend
- [frontend/docs/CONTRATS_API_MANQUANTS.md](../../frontend/docs/CONTRATS_API_MANQUANTS.md) - Contrats API

---

*Document généré par Mistral Vibe*
*Date : 9 novembre 2026*
*Co-Authored-By: Mistral Vibe <vibe@mistral.ai>*
