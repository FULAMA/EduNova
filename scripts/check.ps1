$ErrorActionPreference = "Stop"

Write-Host "=== EduNova Engineering Check ===" -ForegroundColor Cyan

Write-Host "`n[1/4] Compilation Python..." -ForegroundColor Yellow
python -m compileall -q src tests
if ($LASTEXITCODE -ne 0) {
    throw "Échec de la compilation Python."
}
Write-Host "OK" -ForegroundColor Green

Write-Host "`n[2/4] Ruff - analyse..." -ForegroundColor Yellow
ruff check src tests

if ($LASTEXITCODE -ne 0) {
    Write-Host "Ruff signale des problèmes de qualité existants." -ForegroundColor Yellow
    Write-Host "Aucune modification automatique n'est effectuée." -ForegroundColor Yellow
} else {
    Write-Host "OK" -ForegroundColor Green
}

Write-Host "`n[3/4] Vérification Git..." -ForegroundColor Yellow
git diff --check

if ($LASTEXITCODE -ne 0) {
    Write-Host "Git signale des problèmes de whitespace existants." -ForegroundColor Yellow
    Write-Host "Aucune modification automatique n'est effectuée." -ForegroundColor Yellow
} else {
    Write-Host "OK" -ForegroundColor Green
}

Write-Host "`n[4/4] Tests..." -ForegroundColor Yellow
pytest -q --basetemp=F:\EduNova\.pytest_tmp

if ($LASTEXITCODE -ne 0) {
    throw "Les tests ont échoué."
}

Write-Host "OK" -ForegroundColor Green

Write-Host "`n=== EDUNOVA CHECK PASSED ===" -ForegroundColor Green
