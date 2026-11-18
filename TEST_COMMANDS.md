# COMMANDES POUR TESTER EDUNOVA

**Date :** 9 novembre 2026  
**Objectif :** Tester la connexion backend-frontend et les fonctionnalités

---

## 🚀 DÉMARRER L'APPLICATION

### Terminal 1 : Backend
```powershell
cd F:\EduNova
.\.venv\Scripts\Activate.ps1
uvicorn src.presentation.api.app:app --reload --port 8017 --host 0.0.0.0
```

### Terminal 2 : Frontend
```powershell
cd F:\EduNova\frontend
npm run dev
```

---

## ✅ TESTER LA CONNEXION BACKEND-FRONTEND

### Méthode 1 : Script automatisé
```powershell
cd F:\EduNova
python test_backend_frontend_connection.py
```

**Résultat attendu :**
```
[OK] Backend demarre avec succes
[OK] CORS configure
[OK] GET /health -> 200
[OK] POST /auth/register-establishment -> 201
[OK] Frontend Config
[SUCCESS] TOUS LES TESTS ONT REUSSI
```

### Méthode 2 : Tests manuels

#### 1. Vérifier le backend
```powershell
curl http://127.0.0.1:8017/health
```
**Attendu :** `{"status":"ok","application":"EduNova"}`

#### 2. Vérifier CORS
```powershell
curl -I -X OPTIONS http://127.0.0.1:8017/health -H "Origin: http://127.0.0.1:5173"
```
**Attendu :** `Access-Control-Allow-Origin: http://127.0.0.1:5173`

#### 3. Tester l'inscription
```powershell
curl -X POST http://127.0.0.1:8017/auth/register-establishment \
  -H "Content-Type: application/json" \
  -d '{"school_name":"Test School","admin_name":"Test Admin","email":"test@example.com","password":"TestPassword123!"}'
```
**Attendu :** Status 201 avec JSON contenant tenant_id, user_id, etc.

---

## 🌐 TESTER VIA LE NAVIGATEUR

### 1. Accéder au frontend
Ouvrir : http://127.0.0.1:5173

### 2. Tester l'inscription
1. Naviguer vers : http://127.0.0.1:5173/register
2. Remplir le formulaire :
   - Nom de l'établissement : `Mon École Test`
   - Nom du responsable : `Jean Dupont`
   - Email : `jean.dupont@test.com`
   - Mot de passe : `TestPassword123!`
   - Confirmer : `TestPassword123!`
3. Cliquer sur "Créer mon établissement"
4. **Attendu :** Redirection vers /login après 3 secondes

### 3. Tester la connexion
1. Sur http://127.0.0.1:5173/login
2. Saisir :
   - Email : `jean.dupont@test.com`
   - Mot de passe : `TestPassword123!`
3. Cliquer sur "Se connecter"
4. **Attendu :**
   - Si mono-tenant : Connexion réussie
   - Si multi-tenant : Page de sélection du tenant
   - Si 2FA : Page de validation 2FA

---

## 🧪 EXÉCUTER LES TESTS FRONTEND

### Tous les tests
```powershell
cd F:\EduNova\frontend
npm test
```
**Attendu :** 190/190 tests PASS

### Build de production
```powershell
cd F:\EduNova\frontend
npm run build
```
**Attendu :** Build SUCCESS

---

## 🔍 DÉBOGUER

### Vérifier les logs du backend
```powershell
cd F:\EduNova
.\.venv\Scripts\Activate.ps1
uvicorn src.presentation.api.app:app --reload --port 8017 --host 0.0.0.0 --log-level debug
```

### Vérifier les logs du frontend
```powershell
cd F:\EduNova\frontend
npm run dev -- --debug
```

### Vérifier les requêtes réseau
1. Ouvrir Chrome DevTools (F12)
2. Onglet "Network"
3. Vérifier les requêtes à http://127.0.0.1:8017
4. Vérifier les headers CORS

---

## 📊 VÉRIFICATIONS CRITIQUES

| Vérification | Commande | Résultat Attendu |
|--------------|----------|------------------|
| Backend démarré | `curl http://127.0.0.1:8017/health` | 200 OK |
| CORS configuré | `curl -I -X OPTIONS http://127.0.0.1:8017/health -H "Origin: http://127.0.0.1:5173"` | Access-Control-Allow-Origin: http://127.0.0.1:5173 |
| Inscription | `curl -X POST .../auth/register-establishment` | 201 Created |
| Frontend tests | `npm test` | 190/190 PASS |
| Frontend build | `npm run build` | SUCCESS |
| Connexion | Script ou navigateur | Fonctionnelle |

---

## 🎯 COMMANDES RAPIDES

### Tout démarrer et tester
```powershell
# Terminal 1
cd F:\EduNova
.\.venv\Scripts\Activate.ps1
uvicorn src.presentation.api.app:app --reload --port 8017 --host 0.0.0.0

# Terminal 2
cd F:\EduNova\frontend
npm run dev

# Terminal 3 (après 5 secondes)
cd F:\EduNova
python test_backend_frontend_connection.py

# Terminal 4 (après le test)
cd F:\EduNova\frontend
npm test
```

---

## ⚠️ PROBLÈMES COURANTS ET SOLUTIONS

### Problème : Port 8017 déjà utilisé
**Solution :**
```powershell
netstat -ano | findstr :8017
# Trouver le PID et le tuer
taskkill /PID <PID> /F
```

### Problème : CORS bloque les requêtes
**Solution :** Vérifier que le backend a bien :
```python
allow_origin_regex=r"http://127\.0\.0\.1:\d+"
```

### Problème : 404 sur les endpoints
**Solution :** Vérifier que l'URL est http://127.0.0.1:8017 et non http://localhost:8017

### Problème : 500 sur /auth/register-establishment
**Solution :** Vérifier que les champs sont : school_name, admin_name, email, password

---

## 📚 DOCUMENTATION

- [docs/v1.2/README.md](docs/v1.2/README.md) - Index
- [docs/v1.2/QUICK_START_GUIDE.md](docs/v1.2/QUICK_START_GUIDE.md) - Guide complet
- [docs/v1.2/MASTER_INDEX.md](docs/v1.2/MASTER_INDEX.md) - Index maître

---

*Document généré par Mistral Vibe*
*Date : 9 novembre 2026*
