function Show-ReviewNotification {
    param([string[]]$Items)
    Add-Type -AssemblyName System.Windows.Forms
    $notif = New-Object System.Windows.Forms.NotifyIcon
    $notif.Icon = [System.Drawing.SystemIcons]::Warning
    $notif.BalloonTipTitle = "EduNova - REVIEW requis"
    $notif.BalloonTipText = "$($Items.Count) changement(s) necessitent ta decision."
    $notif.Visible = $true
    $notif.ShowBalloonTip(8000)
    Start-Sleep -Seconds 1
    $notif.Dispose()
}
