#!/usr/bin/env powershell
# Script de vérification rapide pour EduNova
# Diagnostique les problèmes de connexion backend/frontend

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  EduNova - Vérification rapide" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = "F:\EduNova"
$FrontendRoot = "$ProjectRoot\frontend"
$Results = @()
$BackendHost = "127.0.0.1"
$Port = 8017
$FrontendPort = 5173

# Test 1 : Vérifier le fichier .env dans le frontend
Write-Host "[TEST 1] Vérification du fichier .env frontend..." -NoNewline
$EnvFile = "$FrontendRoot\.env"
if (Test-Path $EnvFile) {
    $EnvContent = Get-Content $EnvFile -Raw
    if ($EnvContent -match "VITE_API_URL=http://127.0.0.1:8017") {
        Write-Host " [OK] Fichier .env correct" -ForegroundColor Green
        $Results += "✅ .env OK"
    } else {
        Write-Host " [ERREUR] VITE_API_URL non configuré" -ForegroundColor Red
        $Results += "❌ .env ERREUR"
    }
} else {
    Write-Host " [ERREUR] Fichier .env introuvable" -ForegroundColor Red
    $Results += "❌ .env MANQUANT"
}

# Test 2 : Vérifier le backend
Write-Host "[TEST 2] Vérification du backend..." -NoNewline
try {
    $Response = Invoke-WebRequest -Uri "http://${BackendHost}:${Port}/health" -Method GET -ErrorAction SilentlyContinue
    if ($Response.StatusCode -eq 200) {
        Write-Host " [OK] Backend accessible sur http://${BackendHost}:${Port}" -ForegroundColor Green
        $Results += "✅ Backend OK"
    } else {
        Write-Host " [ERREUR] Backend retourne code $($Response.StatusCode)" -ForegroundColor Red
        $Results += "❌ Backend ERREUR"
    }
} catch {
    Write-Host " [ERREUR] Backend non accessible" -ForegroundColor Red
    $Results += "❌ Backend NON ACCESSIBLE"
}

# Test 3 : Vérifier CORS
Write-Host "[TEST 3] Vérification CORS..." -NoNewline
try {
    $Response = Invoke-WebRequest -Uri "http://${BackendHost}:${Port}/health" -Method OPTIONS \
        -Headers @{"Origin"="http://127.0.0.1:5173"; "Access-Control-Request-Method"="GET"} \
        -ErrorAction SilentlyContinue
    $CorsHeader = $Response.Headers["Access-Control-Allow-Origin"]
    if ($CorsHeader -and $CorsHeader -match "http://127.0.0.1") {
        Write-Host " [OK] CORS configuré" -ForegroundColor Green
        $Results += "✅ CORS OK"
    } else {
        Write-Host " [AVERTISSEMENT] CORS non configuré pour le frontend" -ForegroundColor Yellow
        $Results += "⚠️ CORS AVERTISSEMENT"
    }
} catch {
    Write-Host " [AVERTISSEMENT] Impossible de vérifier CORS" -ForegroundColor Yellow
    $Results += "⚠️ CORS AVERTISSEMENT"
}

# Test 4 : Vérifier le endpoint d'inscription
Write-Host "[TEST 4] Vérification endpoint /auth/register-establishment..." -NoNewline
try {
    $Body = @{
        school_name = "Test School"
        admin_name = "Test Admin"
        email = "test_$(Get-Random -Minimum 1 -Maximum 9999)@example.com"
        password = "TestPass123!"
    } | ConvertTo-Json
    
    $Response = Invoke-WebRequest -Uri "http://${BackendHost}:${Port}/auth/register-establishment" \
        -Method POST -Body $Body -ContentType "application/json" -ErrorAction SilentlyContinue
    
    if ($Response.StatusCode -eq 201) {
        Write-Host " [OK] Endpoint accessible" -ForegroundColor Green
        $Results += "✅ Inscription OK"
    } else {
        Write-Host " [ERREUR] Code $($Response.StatusCode)" -ForegroundColor Red
        $Results += "❌ Inscription ERREUR"
    }
} catch {
    Write-Host " [ERREUR] Endpoint non accessible" -ForegroundColor Red
    $Results += "❌ Inscription ERREUR"
}

# Test 5 : Vérifier le endpoint de login
Write-Host "[TEST 5] Vérification endpoint /auth/login..." -NoNewline
try {
    $Body = @{
        email = "test@example.com"
        password = "TestPass123!"
    } | ConvertTo-Json
    
    $Response = Invoke-WebRequest -Uri "http://${BackendHost}:${Port}/auth/login" \
        -Method POST -Body $Body -ContentType "application/json" -ErrorAction SilentlyContinue
    
    if ($Response.StatusCode -eq 200 -or $Response.StatusCode -eq 401) {
        Write-Host " [OK] Endpoint accessible" -ForegroundColor Green
        $Results += "✅ Login OK"
    } else {
        Write-Host " [ERREUR] Code $($Response.StatusCode)" -ForegroundColor Red
        $Results += "❌ Login ERREUR"
    }
} catch {
    Write-Host " [ERREUR] Endpoint non accessible" -ForegroundColor Red
    $Results += "❌ Login ERREUR"
}

# Test 6 : Vérifier le frontend
Write-Host "[TEST 6] Vérification frontend..." -NoNewline
try {
    $Response = Invoke-WebRequest -Uri "http://127.0.0.1:$FrontendPort" -Method GET -ErrorAction SilentlyContinue
    if ($Response.StatusCode -eq 200) {
        Write-Host " [OK] Frontend accessible sur http://127.0.0.1:$FrontendPort" -ForegroundColor Green
        $Results += "✅ Frontend OK"
    } else {
        Write-Host " [ERREUR] Frontend retourne code $($Response.StatusCode)" -ForegroundColor Red
        $Results += "❌ Frontend ERREUR"
    }
} catch {
    Write-Host " [AVERTISSEMENT] Frontend non accessible" -ForegroundColor Yellow
    $Results += "⚠️ Frontend NON DEMARRE"
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Résultats" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

foreach ($Result in $Results) {
    if ($Result -match "✅") {
        Write-Host "  $Result" -ForegroundColor Green
    } elseif ($Result -match "❌") {
        Write-Host "  $Result" -ForegroundColor Red
    } else {
        Write-Host "  $Result" -ForegroundColor Yellow
    }
}

Write-Host ""

# Statistiques
$PassCount = ($Results | Where-Object { $_ -match "✅" }).Count
$FailCount = ($Results | Where-Object { $_ -match "❌" }).Count
$WarnCount = ($Results | Where-Object { $_ -match "⚠️" }).Count

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Statistiques : $PassCount ✅ | $FailCount ❌ | $WarnCount ⚠️" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

if ($FailCount -eq 0) {
    Write-Host ""
    Write-Host "  ✅ Tout est correct !" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Vous pouvez utiliser EduNova à : http://127.0.0.1:5173" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "  ❌ Problèmes détectés" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Consultez les messages d'erreur ci-dessus pour résoudre les problèmes." -ForegroundColor Yellow
    Write-Host "  Vérifiez aussi que :" -ForegroundColor Yellow
    Write-Host "    1. Le backend est démarré (uvicorn ...)" -ForegroundColor Yellow
    Write-Host "    2. Le frontend est démarré (npm run dev)" -ForegroundColor Yellow
    Write-Host "    3. Le fichier .env existe dans le frontend" -ForegroundColor Yellow
    Write-Host "    4. Le backend écoute sur 0.0.0.0:8017" -ForegroundColor Yellow
}
