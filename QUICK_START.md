# 🚀 EduNova - Guide de Démarrage Rapide

## Prérequis

- Python 3.13+
- Node.js 18+
- Git

## Installation

### Backend

```bash
# Cloner le dépôt (si ce n'est pas déjà fait)
git clone <repo-url>
cd EduNova

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Installer les dépendances
pip install -e .
```

### Frontend

```bash
cd frontend
npm install
cd ..
```

## Démarrage

### Option 1: Scripts Prêts à l'Emploi (Recommandé)

**Windows:**
```powershell
.\start_backend.ps1
```

**Linux/macOS/WSL:**
```bash
./start_backend.sh
```

**Frontend (dans un autre terminal):**
```bash
cd frontend
npm run dev
```

### Option 2: Commandes Manuelles

**Backend:**
```bash
# Windows:
$env:EDUNOVA_ENVIRONMENT="development"
$env:EDUNOVA_JWT_SECRET="dev-secret-key-32-chars-minimum-123456789012"
$env:EDUNOVA_DATABASE_PATH="edunova_test.db"
uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017 --reload

# Linux/macOS:
export EDUNOVA_ENVIRONMENT=development
export EDUNOVA_JWT_SECRET="dev-secret-key-32-chars-minimum-123456789012"
export EDUNOVA_DATABASE_PATH="edunova_test.db"
uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017 --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## Accès

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | `http://127.0.0.1:8017` | API REST EduNova |
| Swagger Docs | `http://127.0.0.1:8017/docs` | Documentation API interactive |
| Frontend | `http://127.0.0.1:5173` | Application web EduNova |

## Vérification

### 1. Le backend est démarré ?
```bash
curl http://127.0.0.1:8017/health
# Doit retourner: {"status": "ok", "application": "EduNova"}
```

### 2. L'inscription fonctionne ?
```bash
curl -X POST http://127.0.0.1:8017/auth/register-establishment \
  -H "Content-Type: application/json" \
  -d '{"school_name":"Mon École","admin_name":"Admin User","email":"admin@monecole.com","password":"MonPassword123!"}'
# Doit retourner: 201 Created
```

### 3. La connexion fonctionne ?
```bash
curl -X POST http://127.0.0.1:8017/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@monecole.com","password":"MonPassword123!"}'
# Doit retourner: 200 OK avec access_token
```

## Résolution des Problèmes

### ❌ "Backend inaccessible. Démarrez l'API puis réessayez."

**Cause:** Le backend n'est pas démarré ou n'est pas accessible.

**Solutions:**
1. Vérifiez que le backend est démarré: `curl http://127.0.0.1:8017/health`
2. Vérifiez que le port est correct: `8017` (par défaut)
3. Vérifiez que la clé JWT est valide: au moins 32 caractères
4. Vérifiez qu'il n'y a pas d'erreur dans la console du backend

### ❌ Erreur JWT Secret

**Cause:** `EDUNOVA_JWT_SECRET` a moins de 32 caractères.

**Solution:** Utilisez une clé valide:
```
EDUNOVA_JWT_SECRET=dev-secret-key-32-chars-minimum-123456789012
```

### ❌ 409 Conflict lors de l'inscription

**Cause:** L'email est déjà utilisé.

**Solution:** Utilisez un email différent ou supprimez la base de données temporaire:
```bash
rm edunova_test.db
```

### ❌ CORS bloquant

**Cause:** Le frontend et le backend ont des origines différentes non configurées.

**Solution:** Vérifiez que `EDUNOVA_CORS_ALLOWED_ORIGINS` inclut:
```
http://localhost:5173,http://127.0.0.1:5173
```

## Bonnes Pratiques

### ✅ Toujours utiliser des bases temporaires

```bash
# Bon:
EDUNOVA_DATABASE_PATH=edunova_test.db
EDUNOVA_DATABASE_PATH=edunova_integration.db

# Mauvais (NE JAMAIS):
EDUNOVA_DATABASE_PATH=edunova.db
EDUNOVA_DATABASE_PATH=edunova_dev.db
```

### ✅ Toujours utiliser des clés JWT valides

```bash
# Bon (32+ caractères):
EDUNOVA_JWT_SECRET=dev-secret-key-32-chars-minimum-123456789012

# Mauvais (moins de 32):
EDUNOVA_JWT_SECRET=short
EDUNOVA_JWT_SECRET=dev-secret-edunova-change-later  # 31 chars!
```

### ✅ Toujours vérifier que le backend est démarré

```bash
curl http://127.0.0.1:8017/health
```

## Structure du Projet

```
EduNova/
├── backend/ (src/)
│   ├── presentation/  # API, routes, contrôleurs
│   ├── application/   # Use cases, DTOs, interfaces
│   ├── domain/        # Entités, services, repositories
│   └── infrastructure/# Implémentations concrètes
├── frontend/
│   ├── src/           # Code React/Vite
│   └── public/        # Assets statiques
├── tests/            # Tests unitaires et d'intégration
└── docs/             # Documentation
```

## Commandes Utiles

| Commande | Description |
|----------|-------------|
| `pytest tests/` | Exécuter tous les tests |
| `pytest tests/ -k "auth"` | Exécuter les tests d'authentification |
| `ruff check src/` | Vérifier le style de code |
| `mypy src/` | Vérifier les types |
| `npm run build` | Builder le frontend pour la production |
| `npm run lint` | Vérifier le linting frontend |

---

**✨ EduNova est prêt à l'emploi !**

Si vous suivez ce guide, tout devrait fonctionner parfaitement. 🎉
