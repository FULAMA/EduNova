#!/usr/bin/env powershell
# Script pour démarrer le backend EduNova sur le port 8017

$ErrorActionPreference = "Stop"

# Charger le venv
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "Virtual environment activé" -ForegroundColor Green
} else {
    Write-Host "Aucun venv trouvé, utilisation de Python global" -ForegroundColor Yellow
}

# Configurer les variables d'environnement
$env:EDUNOVA_ENVIRONMENT = "development"
$env:EDUNOVA_JWT_SECRET = "dev-secret-edunova-change-later"
$env:EDUNOVA_ACCESS_TOKEN_EXPIRE_MINUTES = "15"
$env:EDUNOVA_REFRESH_TOKEN_EXPIRE_DAYS = "7"
$env:EDUNOVA_DATABASE_PATH = "edunova_dev.db"
$env:EDUNOVA_CORS_ALLOWED_ORIGINS = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
$env:EDUNOVA_DEV_SEED = "true"
$env:EDUNOVA_DEV_SEED_PASSWORD = "EduNova@2026"
$env:EDUNOVA_DEV_SEED_EMAIL = "admin@edunova.com"

Write-Host "Démarrage du backend EduNova sur http://127.0.0.1:8017..." -ForegroundColor Cyan
Write-Host "Utilisateur: admin@edunova.com / Mot de passe: EduNova@2026 / Tenant: 00000000-0000-0000-0000-000000000001" -ForegroundColor Cyan

# Démarrer avec uvicorn
uvicorn src.presentation.api.main:app --host 127.0.0.1 --port 8017 --reload
