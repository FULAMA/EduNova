# EDUNOVA - Guide de Dépannage

## Problèmes Communs et Solutions

### 🔴 Erreur : "La cle JWT doit contenir au moins 32 caracteres"

**Symptômes** :
```
ValueError: La cle JWT doit contenir au moins 32 caracteres.
```

**Causes** :
1. La variable `EDUNOVA_JWT_SECRET` n'est pas définie dans l'environnement
2. La variable est définie mais contient moins de 32 caractères
3. Le fichier `.env` n'est pas chargé par l'application

**Solutions** :

#### Solution 1 : Vérifier la longueur du JWT Secret
```powershell
# Dans PowerShell
$secret = "votre_secret_ici"
$secret.Length  # Doit être >= 32
```

#### Solution 2 : Définir explicitement la variable dans PowerShell
```powershell
$env:EDUNOVA_JWT_SECRET = "dev-secret-key-32-chars-minimum-123456789012"
# Vérifier
$env:EDUNOVA_JWT_SECRET.Length  # Doit afficher >= 32
```

#### Solution 3 : Vérifier tous les fichiers .env*
```bash
# Vérifier la longueur du JWT secret dans chaque fichier
grep "EDUNOVA_JWT_SECRET" .env* | while read line; do
  secret=$(echo $line | cut -d= -f2)
  echo "$line -> length: ${#secret}"
done
```

**Tous les secrets doivent avoir au moins 32 caractères**

#### Solution 4 : Utiliser les scripts de démarrage
Utilisez toujours `start.ps1`, `start_backend.ps1` ou `start_frontend.ps1` pour démarrer l'application. Ces scripts :
- Définissent correctement les variables d'environnement
- Vérifient la longueur du JWT secret
- Chargent le fichier `.env` avec python-dotenv

#### Solution 5 : Vérifier le fichier .env
Ouvrez `F:/EduNova/.env` et vérifiez que :
```
EDUNOVA_JWT_SECRET=dev-secret-key-32-chars-minimum-12345678901234
```
Contient bien au moins 32 caractères.

---

### 🔴 Erreur : "Backend inaccessible. Démarrez l'API puis réessayez."

**Symptômes** :
- Le frontend affiche ce message
- Le backend ne répond pas aux requêtes

**Causes** :
1. Le backend n'est pas démarré
2. Le backend a démarré mais avec une erreur (ex: JWT secret invalide)
3. Le frontend pointe vers la mauvaise URL
4. Problème CORS
5. Port bloqué

**Solutions** :

#### Solution 1 : Démarrer le backend
```powershell
cd F:/EduNova
./start_backend.ps1
```

Vérifiez que le backend affiche :
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

#### Solution 2 : Vérifier l'URL du frontend
Ouvrez `F:/EduNova/frontend/.env` ou `F:/EduNova/frontend/.env.development` et vérifiez :
```
VITE_API_URL=http://127.0.0.1:8017
```

#### Solution 3 : Tester la connexion manuellement
```powershell
# Tester l'endpoint /health
Invoke-WebRequest -Uri "http://127.0.0.1:8017/health" -Method Get
```

Si cette commande échoue, le backend n'est pas démarré ou écoute sur un autre port.

#### Solution 4 : Vérifier les logs du backend
Si le backend échoue au démarrage, il affiche l'erreur dans la console. Les erreurs courantes :
- JWT secret trop court (voir ci-dessus)
- Base de données inaccessible
- Port déjà utilisé

#### Solution 5 : Vérifier le port
```powershell
# Voir si le port 8017 est utilisé
netstat -ano | Select-String "8017"
```

Si le port est utilisé par un autre processus :
```powershell
# Trouver le PID
$pid = (netstat -ano | Select-String "8017").Line.Split()[-1]
# Tuer le processus
Stop-Process -Id $pid -Force
```

#### Solution 6 : Vérifier le CORS
Assurez-vous que le frontend est dans les origines autorisées :
```
EDUNOVA_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173
```

---

### 🟡 Avertissement : "python-dotenv non disponible"

**Symptômes** :
```
[AVERTISSEMENT] python-dotenv non disponible
```

**Causes** :
Le package `python-dotenv` n'est pas installé.

**Solution** :
```bash
pip install python-dotenv
```

Cependant, ce n'est pas critique car les scripts définissent les variables explicitement.

---

### 🟡 Problème : Les variables d'environnement ne sont pas propagées

**Symptômes** :
- Le backend échoue avec JWT secret vide
- Les variables définies dans PowerShell ne sont pas visibles dans Python

**Cause** :
Les variables définies dans PowerShell avec `$env:VAR=value` ne sont pas automatiquement propagées aux processus enfants.

**Solution** :
Utilisez toujours les scripts de démarrage (`start.ps1`, `start_backend.ps1`, `start_frontend.ps1`) qui :
1. Définissent les variables dans le processus courant
2. Passe les variables explicitement aux processus enfants

---

### 🟢 Test : Vérifier la configuration

Exécutez ce script pour valider la configuration :
```powershell
cd F:/EduNova
python test_config.py
```

**Résultat attendu** :
```
JWT Secret: dev-secret-key-32-chars-minimum-123456789012
JWT Secret length: 44
OK: JWT secret is valid
Settings loaded successfully
JWT Secret from settings: 44 chars
OK: JwtService created successfully
All configuration checks passed!
```

Si ce test échoue, corrigez la configuration avant de démarrer l'application.

---

## Commandes de Diagnostic

### Vérifier les variables d'environnement actuelles
```powershell
# PowerShell
Get-ChildItem Env:

# Ou pour une variable spécifique
$env:EDUNOVA_JWT_SECRET
$env:EDUNOVA_DATABASE_PATH
```

### Vérifier les ports ouverts
```powershell
netstat -ano | Select-String "8017\|5173"
```

### Tester la connexion au backend
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8017/health" -Method Get
```

### Vérifier que python-dotenv est installé
```bash
pip list | grep dotenv
# ou
pip show python-dotenv
```

### Tester l'import des modules
```bash
cd F:/EduNova
python -c "from src.infrastructure.config.settings import Settings; print('OK')"
```

---

## Checklist de Démarrage

### ✅ Avant de Démarrer

- [ ] Python 3.13 est installé
- [ ] Node.js est installé (pour le frontend)
- [ ] Les dépendances sont installées : `pip install -e .`
- [ ] Les dépendances frontend sont installées : `cd frontend && npm install`
- [ ] Le port 8017 est disponible
- [ ] Le port 5173 est disponible
- [ ] Le fichier `.env` existe et contient un JWT secret valide

### ✅ Démarrage du Backend

- [ ] Exécuter `./start_backend.ps1`
- [ ] Voir "Application startup complete"
- [ ] Tester `http://127.0.0.1:8017/health` retourne 200 OK
- [ ] Tester `http://127.0.0.1:8017/docs` affiche Swagger

### ✅ Démarrage du Frontend

- [ ] Exécuter `./start_frontend.ps1`
- [ ] Voir "Local: http://127.0.0.1:5173"
- [ ] Ouvrir le navigateur et accéder à http://127.0.0.1:5173
- [ ] Vérifier qu'il n'y a pas de message "Backend inaccessible"

### ✅ Test des Fonctionnalités

- [ ] Inscription d'un établissement
- [ ] Connexion avec un compte existant
- [ ] Sélection du tenant (si multi-tenant)
- [ ] Authentification 2FA (si activée)
- [ ] Accès à l'espace personnel

---

## Problèmes Courants par Environnement

### Windows (PowerShell)

**Problème** : `start.cmd` ne fonctionne pas
**Solution** : Utiliser `./start.ps1` à la place

**Problème** : Erreur de syntaxe dans start.ps1
**Solution** : Vérifier que le fichier utilise le bon encodage (UTF-8 sans BOM)

**Problème** : uvicorn n'est pas trouvé
**Solution** : Vérifier que le venv est activé ou installer uvicorn : `pip install uvicorn`

### Linux/macOS (Bash)

Les scripts PowerShell ne fonctionnent pas sous Linux/macOS. Utilisez plutôt :

```bash
# Backend
cd /path/to/EduNova
export EDUNOVA_JWT_SECRET="dev-secret-key-32-chars-minimum-123456789012"
export EDUNOVA_ENVIRONMENT="development"
uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017 --reload

# Frontend
cd /path/to/EduNova/frontend
npm run dev
```

---

## Fichiers Importants

| Fichier | Description | Action |
|---------|-------------|--------|
| `.env` | Configuration par défaut | Vérifier JWT_SECRET |
| `.env.backend` | Configuration backend alternative | Vérifier JWT_SECRET |
| `start.ps1` | Script de démarrage complet | Utiliser pour démarrer |
| `start_backend.ps1` | Script de démarrage backend | Utiliser pour backend seul |
| `start_frontend.ps1` | Script de démarrage frontend | Utiliser pour frontend seul |
| `test_config.py` | Test de configuration | Exécuter pour valider |

---

## Messages d'Erreur et Signification

| Message | Cause | Solution |
|---------|-------|----------|
| `La cle JWT doit contenir au moins 32 caracteres` | JWT secret trop court | Allonger le secret |
| `Backend inaccessible` | Backend non démarré ou URL incorrecte | Démarrer backend, vérifier URL |
| `ModuleNotFoundError: No module named 'src'` | PYTHONPATH incorrect | Utiliser les scripts de démarrage |
| `Address already in use` | Port déjà utilisé | Changer de port ou tuer le processus |
| `Connection refused` | Backend non démarré | Démarrer le backend |
| `403 Forbidden` | Problème CORS | Vérifier CORS_ALLOWED_ORIGINS |

---

## Support

Si le problème persiste après avoir essayé toutes les solutions ci-dessus :

1. Exécutez `test_config.py` et partagez le résultat
2. Exécutez le backend et partagez les logs complets
3. Vérifiez la version de Python : `python --version`
4. Vérifiez les packages installés : `pip list`

---

## Historique des Problèmes Résolus

| Date | Problème | Solution |
|------|----------|----------|
| 2025-XX-XX | JWT secret trop court dans .env.backend | Allongé à 35+ caractères |
| 2025-XX-XX | Variables non propagées à uvicorn | Utilisation de scripts dédiés |
| 2025-XX-XX | Backend inaccessible depuis frontend | Vérification CORS et URL |
| 2025-XX-XX | python-dotenv non chargé | Ajout dans les scripts de démarrage |
