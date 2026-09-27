function Get-ReviewSignals {
    $gitStatus = @(git status --short)
    $migrationChanges = @($gitStatus | Where-Object { $_ -match "migrations" -or $_ -match "migration" })
    $domainChanges = @($gitStatus | Where-Object {
        $_ -match "src[/\\](academic|identity|tenancy)[/\\].*domain" -or $_ -match "src[/\\].*domain"
    })
    return [PSCustomObject]@{
        RawStatus        = $gitStatus
        MigrationChanges = $migrationChanges
        DomainChanges    = $domainChanges
        HasReview        = ($migrationChanges.Count -gt 0 -or $domainChanges.Count -gt 0)
    }
}

function Invoke-Work {
    param([switch]$Force)
    Write-Title "EDUNOVA WORK"

    Write-Host "`n[1/6] Verification des signaux REVIEW..." -ForegroundColor Cyan
    $signals = Get-ReviewSignals

    if ($signals.HasReview -and -not $Force) {
        Write-Host "`n[REVIEW] Changements necessitant une decision humaine detectes." -ForegroundColor Magenta
        if ($signals.MigrationChanges.Count -gt 0) {
            Write-Host "`n  Migrations :" -ForegroundColor Yellow
            $signals.MigrationChanges | ForEach-Object { Write-Host "    $_" }
        }
        if ($signals.DomainChanges.Count -gt 0) {
            Write-Host "`n  Domaine :" -ForegroundColor Yellow
            $signals.DomainChanges | ForEach-Object { Write-Host "    $_" }
        }

        $notifyScript = Join-Path $ProjectRoot "scripts\notify-review.ps1"
        if (Test-Path $notifyScript) {
            . $notifyScript
            Show-ReviewNotification -Items ($signals.MigrationChanges + $signals.DomainChanges)
        }

        Write-Host "`nEDUNOVA WORK s'arrete ici. Utilise -Force pour continuer quand meme." -ForegroundColor Red
        return
    }

    if ($signals.HasReview -and $Force) {
        Write-Host "`n[WARN] REVIEW ignore via -Force (decision assumee)." -ForegroundColor Yellow
    } else {
        Write-Host "  [OK] Aucun signal REVIEW." -ForegroundColor Green
    }

    $steps = @(
        @{ Name = "Compilation"; Action = { Invoke-Compile } },
        @{ Name = "Qualite";     Action = { Invoke-Quality } },
        @{ Name = "Securite";    Action = { Invoke-Security } },
        @{ Name = "Tests";       Action = { Invoke-Test } }
    )
    $i = 2
    foreach ($step in $steps) {
        Write-Host "`n[$i/6] $($step.Name)..." -ForegroundColor Cyan
        try { & $step.Action } catch {
            Write-Host "`n[FAIL] $($step.Name) a echoue : $_" -ForegroundColor Red
            return
        }
        $i++
    }

    Write-Host "`n[6/6] Rapport..." -ForegroundColor Cyan
    Invoke-Report
    Write-Host "`n=== EDUNOVA WORK TERMINE ===" -ForegroundColor Green
}

function Invoke-Report {
    Write-Title "EDUNOVA REPORT"
    $reportsDir = Join-Path $ProjectRoot "reports"
    if (-not (Test-Path $reportsDir)) { New-Item -ItemType Directory -Path $reportsDir | Out-Null }
    $timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
    $reportPath = Join-Path $reportsDir "edunova-report-$timestamp.md"
    $signals = Get-ReviewSignals

    $lines = @(
        "# EduNova - Rapport technique", "",
        "Genere le : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')", "",
        "## Git", "",
        "- Entrees modifiees/non suivies : $($signals.RawStatus.Count)",
        "- Changements migrations (REVIEW) : $($signals.MigrationChanges.Count)",
        "- Changements domaine (REVIEW) : $($signals.DomainChanges.Count)", ""
    )
    $lines -join "`n" | Out-File -FilePath $reportPath -Encoding UTF8
    Write-Host "`nRapport ecrit : $reportPath" -ForegroundColor Green
}

function Invoke-Auto {
    Write-Title "EDUNOVA AUTO"
    Write-Host "Mode non-supervise : taches SAFE uniquement, jamais de -Force." -ForegroundColor Cyan
    Invoke-Work
}
