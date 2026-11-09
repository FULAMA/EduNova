#!/usr/bin/env powershell
# Script de démarrage du backend EduNova pour Windows
# Utilise une base de données temporaire et une clé JWT valide

$ErrorActionPreference = "Stop"

# Chemin du projet
$ProjectRoot = "F:\EduNova"
Set-Location -Path $ProjectRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  EduNova - Démarrage Backend" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$BackendHost = "0.0.0.0"
$Port = 8017
$DbPath = "$ProjectRoot\edunova_test.db"
$JwtSecret = "dev-secret-key-32-chars-minimum-123456789012"  # 44 caractères

# Définir les variables d'environnement
$env:EDUNOVA_ENVIRONMENT = "development"
$env:EDUNOVA_JWT_SECRET = $JwtSecret
$env:EDUNOVA_DATABASE_PATH = $DbPath
$env:EDUNOVA_ACCESS_TOKEN_EXPIRE_MINUTES = "15"
$env:EDUNOVA_REFRESH_TOKEN_EXPIRE_DAYS = "7"
$env:EDUNOVA_CORS_ALLOWED_ORIGINS = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
$env:EDUNOVA_DEV_SEED = "true"
$env:EDUNOVA_DEV_SEED_PASSWORD = "DevPass123!"
$env:EDUNOVA_DEV_SEED_EMAIL = "admin@edunova.com"

Write-Host "[CONFIG] Variables d'environnement configurées" -ForegroundColor Yellow
Write-Host "[CONFIG] JWT Secret : $($JwtSecret.Length) caractères" -ForegroundColor Yellow
Write-Host "[CONFIG] Base de données : $DbPath" -ForegroundColor Yellow
Write-Host "[CONFIG] Port : $Port" -ForegroundColor Yellow
Write-Host ""

# Créer la base de données si elle n'existe pas
if (-not (Test-Path $DbPath)) {
    Write-Host "[SETUP] Création de la base de données $DbPath..." -ForegroundColor Yellow
    New-Item -Path $DbPath -ItemType File -Force | Out-Null
    Write-Host "  [OK] Base de données créée" -ForegroundColor Green
} else {
    Write-Host "[SETUP] Base de données $DbPath existe déjà" -ForegroundColor Green
}

Write-Host ""

# Démarrer le backend
Write-Host "[START] Démarrage du backend FastAPI..." -ForegroundColor Yellow
Write-Host "  URL : http://${BackendHost}:${Port}" -ForegroundColor DarkGray
Write-Host "  Swagger : http://${BackendHost}:${Port}/docs" -ForegroundColor DarkGray
Write-Host ""

try {
    # Exécuter uvicorn avec les variables définies
    uvicorn src.presentation.api.main:app --host $BackendHost --port $Port --reload
} catch {
    Write-Host "[ERREUR] Impossible de démarrer le backend : $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vérifiez que :" -ForegroundColor Yellow
    Write-Host "  1. Python 3.13 est installé" -ForegroundColor Yellow
    Write-Host "  2. Les dépendances sont installées (pip install -e .)" -ForegroundColor Yellow
    Write-Host "  3. Le port $Port est disponible" -ForegroundColor Yellow
    exit 1
}
