# start.ps1 — lance backend (8001) + frontend (5173)
$root = $PSScriptRoot

Write-Host "Starting Macro Terminal..." -ForegroundColor Cyan

# Kill any existing instances on these ports
$pids8001 = (netstat -ano | findstr "LISTEN" | findstr ":8001 ") -split '\s+' | Where-Object { $_ -match '^\d+$' } | Select-Object -Last 1
if ($pids8001) { Stop-Process -Id $pids8001 -Force -ErrorAction SilentlyContinue }
$pids5173 = (netstat -ano | findstr "LISTEN" | findstr ":5173 ") -split '\s+' | Where-Object { $_ -match '^\d+$' } | Select-Object -Last 1
if ($pids5173) { Stop-Process -Id $pids5173 -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 1

# Backend
Write-Host "  Backend  -> http://localhost:8001" -ForegroundColor Green
Start-Process -FilePath "py" -ArgumentList "-m uvicorn backend.main:app --port 8001" -WorkingDirectory $root -WindowStyle Hidden

# Frontend
Write-Host "  Frontend -> http://localhost:5173" -ForegroundColor Green
Start-Process -FilePath "cmd" -ArgumentList "/c npm run dev" -WorkingDirectory "$root\frontend" -WindowStyle Hidden

Start-Sleep -Seconds 6

$b = Invoke-RestMethod http://localhost:8001/api/health -ErrorAction SilentlyContinue
if ($b.status -eq "ok") {
    Write-Host "`nReady! Open http://localhost:5173" -ForegroundColor Cyan
    Start-Process "http://localhost:5173"
} else {
    Write-Host "Backend not responding - check for errors" -ForegroundColor Red
}
