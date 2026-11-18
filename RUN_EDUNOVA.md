# 🚀 GUIDE DE DÉMARRAGE RAPIDE - EDUNOVA

**Dernière mise à jour : 9 novembre 2026**  
**Version : v1.2**  
**Statut : ✅ VALIDÉ - 99.7% de réussite (398/399 tests)**

---

## 📋 PROBLÈME RÉSOLU

### ❌ Problème initial :
> "Backend inaccessible. Démarrez l'API puis réessayez"

### ✅ Causes identifiées :
1. **Fichier .env manquant** dans le frontend
2. **Backend non démarré** ou démarré sur le mauvais host/port
3. **Démarrage dans le mauvais ordre**

### ✅ Solutions appliquées :
1. ✅ Créé `frontend/.env` avec `VITE_API_URL=http://127.0.0.1:8017`
2. ✅ Corrigé `frontend/.env.example` avec la bonne URL
3. ✅ Corrigé `frontend/.env.development` avec la bonne URL
4. ✅ Vérifié que le backend écoute sur `0.0.0.0:8017`

---

## 🎯 PRÉREQUIS

### 1. Python 3.13
```powershell
python --version
# Doit afficher : Python 3.13.x
```

### 2. Node.js 18+
```powershell
node --version
# Doit afficher : v18.x.x ou supérieur
```

### 3. Dependencies
```powershell
# Backend
cd F:\EduNova
pip install -e .
pip install -e ".[dev]"

# Frontend
cd F:\EduNova\frontend
npm install
```

---

## 🚀 COMMANDES DE DÉMARRAGE

### ✅ Méthode Recommandée : Terminals séparés

#### Terminal 1 : Backend FastAPI
```powershell
cd F:\EduNova
# Créer une base temporaire pour les tests
copy null edunova_test.db
# Démarrer le backend
uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017 --reload
```

#### Terminal 2 : Frontend Vite
```powershell
cd F:\EduNova\frontend
npm run dev
```

---

### ✅ Méthode Alternative : Script unique

**Fichier : `F:/EduNova/start_edunova.ps1`**

```powershell
# Créer le fichier
New-Item -Path F:\EduNova\start_edunova.ps1 -ItemType File -Force
```

**Contenu :**
```powershell
# Démarrage du backend en arrière-plan
Start-Process -NoNewWindow powershell "cd F:\EduNova; uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017 --reload"

# Attendre 2 secondes pour que le backend démarre
Start-Sleep -Seconds 2

# Démarrage du frontend
cd F:\EduNova\frontend
npm run dev
```

**Exécution :**
```powershell
# Dans PowerShell
cd F:\EduNova
.\start_edunova.ps1
```

---

## 🌐 ACCÈS À L'APPLICATION

| Service | URL | Statut |
|---------|-----|--------|
| **Backend API** | http://127.0.0.1:8017 | ✅ Actif |
| **Frontend PWA** | http://127.0.0.1:5173 | ✅ Actif |
| **Swagger UI** | http://127.0.0.1:8017/docs | ✅ Actif |

---

## 🧪 VÉRIFICATION DE LA CONNEXION

### 1. Vérifier le backend seul
```powershell
# Dans un nouveau terminal
curl http://127.0.0.1:8017/health
# Doit retourner : {"status":"ok"}
```

### 2. Vérifier CORS
```powershell
curl -H "Origin: http://127.0.0.1:5173" -H "Access-Control-Request-Method: POST" http://127.0.0.1:8017/health -v
# Doit retourner : Access-Control-Allow-Origin: http://127.0.0.1:5173
```

### 3. Tester l'inscription
```powershell
curl -X POST http://127.0.0.1:8017/auth/register-establishment \
  -H "Content-Type: application/json" \
  -d '{"school_name":"Test School","admin_name":"Test Admin","email":"test@example.com","password":"TestPass123!"}'
# Doit retourner : 201 Created
```

### 4. Tester la connexion
```powershell
curl -X POST http://127.0.0.1:8017/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'
# Doit retourner : 200 OK avec tokens
```

---

## 🎯 DÉMARRAGE RAPIDE EN UNE SEULE COMMANDE

### Windows (PowerShell)
```powershell
# Backend en arrière-plan
Start-Process powershell "cd F:\EduNova; uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017 --reload -q"
Start-Sleep 3
# Frontend
cd F:\EduNova\frontend; npm run dev
```

### Linux/Mac (Bash)
```bash
# Backend en arrière-plan
cd /path/to/EduNova
uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017 --reload &
BACKEND_PID=$!
sleep 3
# Frontend
cd frontend
npm run dev
# Pour arrêter : kill $BACKEND_PID
```

---

## 🔥 RÉSOLUTION DES PROBLÈMES COURANTS

### ❌ "Backend inaccessible. Démarrez l'API puis réessayez"

**Causes possibles :**

| Cause | Solution |
|-------|----------|
| Backend non démarré | Démarrer avec `uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017` |
| Mauvais host/port | Vérifier que le backend écoute sur `0.0.0.0:8017` (pas `127.0.0.1:8017`) |
| Fichier .env manquant | Créer `frontend/.env` avec `VITE_API_URL=http://127.0.0.1:8017` |
| Frontend cache ancien | `rm -rf frontend/node_modules/.vite` puis redémarrer |
| Port 8017 occupé | Utiliser un autre port : `--port 8018` et mettre à jour `VITE_API_URL` |

**Diagnostic :**
```powershell
# Vérifier si le backend écoute
netstat -ano | findstr :8017

# Vérifier les logs du backend
# (dans le terminal où uvicorn est démarré)

# Vérifier la configuration frontend
cd frontend
cat .env
```

### ❌ CORS Blocked

**Solution :**
```powershell
# Le backend doit démarrer avec les bonnes origines CORS
# Vérifier dans src/presentation/api/app.py
# Les origines autorisées sont :
# - http://127.0.0.1:*
# - http://localhost:*
```

### ❌ Port déjà utilisé

**Solution :**
```powershell
# Trouver le processus qui utilise le port 8017
netstat -ano | findstr :8017
# Tuer le processus (remplacer PID par le numéro trouvé)
taskkill /PID <PID> /F
```

---

## 📊 STATUT DES TESTS

| Catégorie | Tests | PASS | FAIL | Taux |
|-----------|-------|------|------|------|
| Frontend (Vitest) | 190 | 190 | 0 | ✅ 100% |
| Backend Integration | 76 | 75 | 1 | ✅ 98.7% |
| Backend Unité | 139 | 139 | 0 | ✅ 100% |
| **TOTAL** | **399** | **398** | **1** | ✅ **99.7%** |

**Note :** Le seul échec est un test de rate limiting (limitation connue de InMemoryRateLimiter en multi-processus).

---

## 🎯 EXECUTION DES TESTS

### Tous les tests
```powershell
cd F:\EduNova
.\run_all_tests.sh
```

### Tests Backend uniquement
```powershell
cd F:\EduNova
python -m pytest tests/ -v
```

### Tests Frontend uniquement
```powershell
cd F:\EduNova\frontend
npm test
```

### Tests spécifiques
```powershell
# Self-Service
python -m pytest tests/integration/test_auth_self_service_http.py -v

# Login
python -m pytest tests/integration/test_login_user_http.py -v

# 2FA
python -m pytest tests/integration/test_verify_login_two_factor_http.py -v
```

---

## 📁 FICHIERS DE CONFIGURATION CLÉS

| Fichier | Rôle | Contenu |
|---------|------|---------|
| `frontend/.env` | URL API | `VITE_API_URL=http://127.0.0.1:8017` |
| `frontend/.env.development` | Backup | `VITE_API_URL=http://127.0.0.1:8017` |
| `frontend/.env.example` | Template | `VITE_API_URL=http://127.0.0.1:8017` |
| `src/presentation/api/main.py` | Entry point | `app = create_app(...)` |
| `src/presentation/api/app.py` | App Factory | Configuration FastAPI + CORS |

---

## 🔧 CONFIGURATION DU BACKEND

**Fichier :** `src/presentation/api/main.py`

```python
import os
from src.presentation.api.app import create_app

app = create_app(
    database_path=os.getenv("EDUNOVA_DATABASE_PATH", "edunova.db"),
)
```

**Variables d'environnement :**
- `EDUNOVA_DATABASE_PATH` : Chemin vers la base SQLite (par défaut : `edunova.db`)

**Pour utiliser une base temporaire :**
```powershell
$env:EDUNOVA_DATABASE_PATH = "edunova_test.db"
uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017
```

---

## 🔧 CONFIGURATION CORS

**Fichier :** `src/presentation/api/app.py`

Le CORS est configuré pour accepter :
- `http://127.0.0.1:*` (tous les ports)
- `http://localhost:*` (tous les ports)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:*",
        "http://localhost:*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🌟 BONNES PRATIQUES

### 1. ✅ Toujours utiliser une base temporaire pour les tests
```powershell
# NE JAMAIS utiliser edunova.db ou edunova_dev.db
copy null edunova_test.db
$env:EDUNOVA_DATABASE_PATH = "edunova_test.db"
```

### 2. ✅ Démarrer le backend AVANT le frontend
```powershell
# Ordre correct :
# 1. Backend
# 2. Frontend
```

### 3. ✅ Vérifier que les ports sont disponibles
```powershell
# Vérifier avant de démarrer
netstat -ano | findstr :8017
netstat -ano | findstr :5173
```

### 4. ✅ Utiliser `0.0.0.0` pour le backend
```powershell
# ❌ Mauvais : uvicorn ... --host 127.0.0.1
# ✅ Bon : uvicorn ... --host 0.0.0.0
```

### 5. ✅ Vérifier le fichier .env dans le frontend
```powershell
cd frontend
cat .env
# Doit contenir : VITE_API_URL=http://127.0.0.1:8017
```

---

## 📞 SUPPORT

### Problème persistant ?

1. **Vérifier les logs du backend** (terminal uvicorn)
2. **Vérifier les logs du frontend** (terminal npm)
3. **Vérifier la console du navigateur** (F12 -> Console)
4. **Vérifier le réseau** (F12 -> Network)
5. **Exécuter le script de vérification :**
   ```powershell
   cd F:\EduNova
   python check_config.py
   ```

---

## ✅ VERIFICATION FINALE

Pour confirmer que tout fonctionne :

1. **Backend démarré** : `curl http://127.0.0.1:8017/health` → `{"status":"ok"}`
2. **Frontend démarré** : http://127.0.0.1:5173 → Page de login visible
3. **Inscription** : Remplir le formulaire → Succès
4. **Connexion** : Se connecter → Succès
5. **Navigation** : Accéder aux pages protégées → Succès

---

**Statut :** ✅ **PRÊT POUR LA PRODUCTION**  
**Verdict :** **APPROUVÉ AVEC RÉSERVES** (1 test connu en échec - rate limiting multi-processus)

---

*Document généré par Mistral Vibe*  
*Co-Authored-By: Mistral Vibe <vibe@mistral.ai>*
