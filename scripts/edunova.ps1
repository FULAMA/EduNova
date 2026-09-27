param(
    [Parameter(Position = 0)]
    [string]$Command = "help"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

function Write-Title($Text) {
    Write-Host "`n=== $Text ===" -ForegroundColor Cyan
}

function Show-Help {
    Write-Host @"

EduNova Engineering CLI

Usage:
    .\scripts\edunova.ps1 <command>

Commands:
    check       Verification complète
    test        Tests complets
    quality     Mypy + Ruff
    security    Bandit + pip-audit
    compile     Compilation Python
    doctor      Diagnostic automatique
    status      État technique rapide
    help        Affiche cette aide

Exemples:
    .\scripts\edunova.ps1 check
    .\scripts\edunova.ps1 test
    .\scripts\edunova.ps1 quality
    .\scripts\edunova.ps1 security
    .\scripts\edunova.ps1 doctor
    .\scripts\edunova.ps1 status

"@
}

function Invoke-Compile {
    Write-Title "COMPILATION"

    python -m compileall -q src tests

    if ($LASTEXITCODE -ne 0) {
        throw "La compilation Python a échoué."
    }

    Write-Host "Compilation OK" -ForegroundColor Green
}

function Invoke-Test {
    Write-Title "TESTS"

    pytest -q --basetemp="$ProjectRoot\.pytest_tmp"

    if ($LASTEXITCODE -ne 0) {
        throw "Les tests ont échoué."
    }

    Write-Host "Tests OK" -ForegroundColor Green
}

function Invoke-Quality {
    Write-Title "QUALITÉ"

    Write-Host "`n--- Mypy ---" -ForegroundColor Yellow
    mypy --explicit-package-bases src

    if ($LASTEXITCODE -ne 0) {
        throw "Mypy a détecté des erreurs."
    }

    Write-Host "`n--- Ruff ---" -ForegroundColor Yellow
    ruff check src tests

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Ruff signale des problèmes existants." -ForegroundColor Yellow
        Write-Host "Aucune modification automatique." -ForegroundColor Yellow
    }

    Write-Host "`nQualité terminée." -ForegroundColor Green
}

function Invoke-Security {
    Write-Title "SÉCURITÉ"

    Write-Host "`n--- Bandit ---" -ForegroundColor Yellow
    bandit -r src -ll

    if ($LASTEXITCODE -ne 0) {
        throw "Bandit a détecté un problème."
    }

    Write-Host "`n--- pip-audit ---" -ForegroundColor Yellow
    pip-audit

    if ($LASTEXITCODE -ne 0) {
        Write-Host "pip-audit signale des dépendances vulnérables." -ForegroundColor Yellow
        Write-Host "Aucune mise à jour automatique de dépendance." -ForegroundColor Yellow
    }

    Write-Host "`nSécurité terminée." -ForegroundColor Green
}

function Invoke-Status {
    Write-Title "EDUNOVA STATUS"

    Write-Host "`nPython:"
    python --version

    Write-Host "`nPytest:"
    pytest --version

    Write-Host "`nMypy:"
    mypy --version

    Write-Host "`nRuff:"
    ruff --version

    Write-Host "`nBandit:"
    bandit --version

    Write-Host "`nGit:"
    git status --short

    Write-Host "`nÉtat technique affiché." -ForegroundColor Green
}

function Invoke-Doctor {
    Write-Title "EDUNOVA DOCTOR"

    $warnings = 0
    $reviews = 0
    $failures = 0

    # ---------------------------------------------------------
    # ENVIRONNEMENT
    # ---------------------------------------------------------

    Write-Host "`n[ENVIRONNEMENT]" -ForegroundColor Cyan

    Write-Host "`nPython:"
    python --version

    Write-Host "`nOutils:"

    $tools = @(
        "python",
        "pytest",
        "mypy",
        "ruff",
        "bandit",
        "pip-audit",
        "git"
    )

    foreach ($tool in $tools) {
        if (Get-Command $tool -ErrorAction SilentlyContinue) {
            Write-Host "[OK] $tool" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] $tool absent" -ForegroundColor Red
            $failures++
        }
    }

    # ---------------------------------------------------------
    # COMPILATION
    # ---------------------------------------------------------

    Write-Host "`n[COMPILATION]" -ForegroundColor Cyan

    python -m compileall -q src tests

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Compilation Python" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Compilation Python" -ForegroundColor Red
        $failures++
    }

    # ---------------------------------------------------------
    # MYPY
    # ---------------------------------------------------------

    Write-Host "`n[TYPES]" -ForegroundColor Cyan

    mypy --explicit-package-bases src

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Mypy" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Mypy" -ForegroundColor Red
        $failures++
    }

    # ---------------------------------------------------------
    # BANDIT
    # ---------------------------------------------------------

    Write-Host "`n[SÉCURITÉ CODE]" -ForegroundColor Cyan

    bandit -r src -ll

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Bandit" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Bandit" -ForegroundColor Red
        $failures++
    }

    # ---------------------------------------------------------
    # PIP AUDIT
    # ---------------------------------------------------------

    Write-Host "`n[DÉPENDANCES]" -ForegroundColor Cyan

    pip-audit

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] pip-audit" -ForegroundColor Green
    } else {
        Write-Host "[WARN] pip-audit signale des vulnérabilités." -ForegroundColor Yellow
        Write-Host "Aucune dépendance ne sera modifiée automatiquement." -ForegroundColor Yellow
        $warnings++
    }

    # ---------------------------------------------------------
    # PIP CHECK
    # ---------------------------------------------------------

    Write-Host "`n[ENVIRONNEMENT PYTHON]" -ForegroundColor Cyan

    pip check

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] pip check" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Conflits de dépendances dans l'environnement Python." -ForegroundColor Yellow
        $warnings++
    }

    # ---------------------------------------------------------
    # RUFF
    # ---------------------------------------------------------

    Write-Host "`n[QUALITÉ CODE]" -ForegroundColor Cyan

    ruff check src tests

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Ruff" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Ruff signale des problèmes." -ForegroundColor Yellow
        Write-Host "Aucune correction automatique." -ForegroundColor Yellow
        $warnings++
    }

    # ---------------------------------------------------------
    # TESTS
    # ---------------------------------------------------------

    Write-Host "`n[TESTS]" -ForegroundColor Cyan

    pytest -q --basetemp="$ProjectRoot\.pytest_tmp"

    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Tests complets" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Tests complets" -ForegroundColor Red
        $failures++
    }

    # ---------------------------------------------------------
    # GIT
    # ---------------------------------------------------------

    Write-Host "`n[GIT]" -ForegroundColor Cyan

    $gitStatus = @(git status --short)

    if ($gitStatus.Count -eq 0) {
        Write-Host "[OK] Aucun changement Git" -ForegroundColor Green
    } else {
        Write-Host "[INFO] $($gitStatus.Count) entrées Git modifiées/non suivies." -ForegroundColor Yellow

        $migrationChanges = @(
            $gitStatus |
            Where-Object {
                $_ -match "migrations" -or
                $_ -match "migration"
            }
        )

        $domainChanges = @(
            $gitStatus |
            Where-Object {
                $_ -match "src[/\\](academic|identity|tenancy)[/\\].*domain" -or
                $_ -match "src[/\\].*domain"
            }
        )

        if ($migrationChanges.Count -gt 0) {
            Write-Host "[REVIEW] $($migrationChanges.Count) changement(s) lié(s) aux migrations." -ForegroundColor Magenta
            $reviews++
        }

        if ($domainChanges.Count -gt 0) {
            Write-Host "[REVIEW] $($domainChanges.Count) changement(s) dans le domaine." -ForegroundColor Magenta
            $reviews++
        }
    }

    # ---------------------------------------------------------
    # MANIFESTE DÉPENDANCES
    # ---------------------------------------------------------

    Write-Host "`n[REPRODUCTIBILITÉ]" -ForegroundColor Cyan

    $dependencyFiles = @(
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        "requirements-test.txt",
        "Pipfile",
        "poetry.lock"
    )

    $foundDependencyFile = $false

    foreach ($file in $dependencyFiles) {
        if (Test-Path $file) {
            $foundDependencyFile = $true
            Write-Host "[OK] $file présent" -ForegroundColor Green
        }
    }

    if (-not $foundDependencyFile) {
        Write-Host "[REVIEW] Aucun manifeste de dépendances détecté." -ForegroundColor Magenta
        Write-Host "La reproductibilité de l'environnement doit être traitée séparément." -ForegroundColor Yellow
        $reviews++
    }

    # ---------------------------------------------------------
    # RÉSUMÉ
    # ---------------------------------------------------------

    Write-Title "DIAGNOSTIC"

    if ($failures -eq 0) {
        Write-Host "[OK] Aucun blocage technique détecté." -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $failures problème(s) bloquant(s)." -ForegroundColor Red
    }

    if ($warnings -gt 0) {
        Write-Host "[WARN] $warnings avertissement(s)." -ForegroundColor Yellow
    } else {
        Write-Host "[OK] Aucun avertissement." -ForegroundColor Green
    }

    if ($reviews -gt 0) {
        Write-Host "[REVIEW] $reviews point(s) nécessitent une décision/revue humaine." -ForegroundColor Magenta
    } else {
        Write-Host "[OK] Aucun point architectural détecté." -ForegroundColor Green
    }

    Write-Host "`nRègle:"
    Write-Host "SAFE       = automatisable"
    Write-Host "WARN       = information à traiter"
    Write-Host "REVIEW     = décision humaine requise"
    Write-Host "FAIL       = blocage technique"

    if ($failures -gt 0) {
        exit 1
    }
}

function Invoke-Check {
    Write-Title "EDUNOVA ENGINEERING CHECK"

    Invoke-Compile
    Invoke-Quality
    Invoke-Security
    Invoke-Test

    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host " EDUNOVA CHECK PASSED" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
}

switch ($Command.ToLower()) {
    "compile"  { Invoke-Compile }
    "test"     { Invoke-Test }
    "quality"  { Invoke-Quality }
    "security" { Invoke-Security }
    "doctor"   { Invoke-Doctor }
    "status"   { Invoke-Status }
    "check"    { Invoke-Check }
    "help"     { Show-Help }
    default    {
        Write-Host "Commande inconnue: $Command" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
