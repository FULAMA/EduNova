#!/bin/bash
# Script de démarrage du backend EduNova
# Utilise une base de données temporaire et une clé JWT valide

# Configuration
export EDUNOVA_ENVIRONMENT=development
export EDUNOVA_JWT_SECRET="dev-secret-key-32-chars-minimum-123456789012"
export EDUNOVA_DATABASE_PATH="edunova_test.db"
export EDUNOVA_ACCESS_TOKEN_EXPIRE_MINUTES=15
export EDUNOVA_REFRESH_TOKEN_EXPIRE_DAYS=7
export EDUNOVA_CORS_ALLOWED_ORIGINS="http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
export EDUNOVA_DEV_SEED=true
export EDUNOVA_DEV_SEED_PASSWORD="DevPass123!"
export EDUNOVA_DEV_SEED_EMAIL="admin@edunova.com"

# Créer la base de données si elle n'existe pas
if [ ! -f "$EDUNOVA_DATABASE_PATH" ]; then
    touch "$EDUNOVA_DATABASE_PATH"
    echo "Base de données créée: $EDUNOVA_DATABASE_PATH"
fi

echo "Démarrage du backend EduNova..."
echo "URL: http://127.0.0.1:8017"
echo "Swagger: http://127.0.0.1:8017/docs"
echo "Base de données: $EDUNOVA_DATABASE_PATH"
echo "Clé JWT: ${#EDUNOVA_JWT_SECRET} caractères"
echo ""

# Démarrer uvicorn
uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8017 --reload
