#!/usr/bin/env powershell
# Script principal pour démarrer EduNova
# Peut être exécuté depuis n'importe quel répertoire

$ErrorActionPreference = "Stop"

# Chemin du projet
$ProjectRoot = "F:\EduNova"

# Changer de répertoire
Set-Location -Path $ProjectRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  EduNova - Démarrage Complet" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ce script démarre le backend et le frontend." -ForegroundColor Gray
Write-Host "Utilisez start_backend.ps1 ou start_frontend.ps1 pour démarrer un seul service." -ForegroundColor Gray
Write-Host ""

# Configuration Backend
$BackendHost = "0.0.0.0"
$BackendPort = 8017
$DbPath = "$ProjectRoot\edunova_test.db"
$JwtSecret = "dev-secret-key-32-chars-minimum-123456789012"

# Vérifier que le JWT secret a au moins 32 caractères
if ($JwtSecret.Length -lt 32) {
    Write-Host "[ERREUR] Le JWT secret doit contenir au moins 32 caracteres. Actuellement: $($JwtSecret.Length)" -ForegroundColor Red
    exit 1
}

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

Write-Host "[CONFIG] Variables d'environnement Backend configurées" -ForegroundColor Yellow
Write-Host "[CONFIG] JWT Secret : $($JwtSecret.Length) caractères" -ForegroundColor Yellow
Write-Host "[CONFIG] Base de données : $DbPath" -ForegroundColor Yellow
Write-Host "[CONFIG] Port Backend : $BackendPort" -ForegroundColor Yellow
Write-Host ""

# Charger le fichier .env avec python-dotenv
try {
    Write-Host "[CONFIG] Chargement du fichier .env avec python-dotenv..." -ForegroundColor Yellow
    python -c "from dotenv import load_dotenv; load_dotenv(); print('OK')" | Out-Null
    Write-Host "[CONFIG] Fichier .env chargé avec python-dotenv" -ForegroundColor Green
} catch {
    Write-Host "[AVERTISSEMENT] python-dotenv non disponible: $_" -ForegroundColor Yellow
}

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
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Démarrage des services..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Démarrer le backend dans un nouveau processus
Write-Host "[START] Démarrage du backend FastAPI sur port $BackendPort..." -ForegroundColor Yellow
Write-Host "  URL : http://${BackendHost}:${BackendPort}" -ForegroundColor DarkGray
Write-Host "  Swagger : http://${BackendHost}:${BackendPort}/docs" -ForegroundColor DarkGray
Write-Host "  Health check : http://${BackendHost}:${BackendPort}/health" -ForegroundColor DarkGray
Write-Host ""

Start-Process -NoNewWindow powershell -ArgumentList "-ExecutionPolicy Bypass -File \"$ProjectRoot\start_backend.ps1\"" -PassThru
Start-Sleep -Seconds 3

# Démarrer le frontend dans un nouveau processus
Write-Host "[START] Démarrage du frontend Vite sur port 5173..." -ForegroundColor Yellow
Write-Host "  URL : http://127.0.0.1:5173" -ForegroundColor DarkGray
Write-Host ""

Start-Process -NoNewWindow powershell -ArgumentList "-ExecutionPolicy Bypass -File \"$ProjectRoot\start_frontend.ps1\"" -PassThru

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Les deux services devraient être démarrés!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://127.0.0.1:$BackendPort" -ForegroundColor Green
Write-Host "Backend Swagger: http://127.0.0.1:$BackendPort/docs" -ForegroundColor Green
Write-Host "Frontend: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Appuyez sur Entrée pour quitter..." -ForegroundColor Gray
Read-Host
