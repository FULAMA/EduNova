#!/usr/bin/env powershell
# Script pour démarrer uniquement le frontend EduNova

$ErrorActionPreference = "Stop"

# Chemin du projet
$ProjectRoot = "F:\EduNova"
$FrontendPath = "$ProjectRoot\frontend"

# Changer de répertoire
Set-Location -Path $FrontendPath

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  EduNova Frontend - Démarrage" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$ApiUrl = "http://127.0.0.1:8017"

# Définir les variables d'environnement pour Vite
$env:VITE_API_URL = $ApiUrl

Write-Host "[CONFIG] API URL : $ApiUrl" -ForegroundColor Yellow
Write-Host "[CONFIG] Frontend URL : http://127.0.0.1:5173" -ForegroundColor Yellow
Write-Host ""

# Vérifier que npm est disponible
try {
    npm --version | Out-Null
    Write-Host "[CHECK] npm est disponible" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] npm n'est pas disponible. Installez Node.js d'abord." -ForegroundColor Red
    exit 1
}

# Démarrer Vite
Write-Host "[START] Démarrage de Vite (React)..." -ForegroundColor Yellow
Write-Host ""

try {
    npm run dev
} catch {
    Write-Host "[ERREUR] Impossible de démarrer le frontend : $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vérifiez que :" -ForegroundColor Yellow
    Write-Host "  1. Node.js est installé" -ForegroundColor Yellow
    Write-Host "  2. Les dépendances sont installées (npm install)" -ForegroundColor Yellow
    Write-Host "  3. Le port 5173 est disponible" -ForegroundColor Yellow
    exit 1
}
