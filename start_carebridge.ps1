# CareBridge AI — Windows PowerShell Launch Script
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Starting CareBridge AI (మీ మందులు, మీ భాష, మీ ఆరోగ్యం)  " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

$nodeDir = (Get-ChildItem "$HOME\.node_portable\node-*" -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
if ($nodeDir) {
    $env:PATH = "$nodeDir;" + $env:PATH
}

Write-Host "Starting CareBridge AI on http://127.0.0.1:5000 ..." -ForegroundColor Yellow
Start-Process "http://127.0.0.1:5000"
python -m backend.app
