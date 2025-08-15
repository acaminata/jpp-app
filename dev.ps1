# dev.ps1
# Requisitos previos:
# - Haber creado los entornos y instalado dependencias:
#   backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
#   frontend\.venv\Scripts\python.exe -m pip install -r frontend\requirements.txt

$ErrorActionPreference = "Stop"

# 1) Variables de entorno para el frontend
$env:BACKEND_URL = "http://localhost:8000"

# 2) Comandos de arranque
$backendCmd  = "backend\.venv\Scripts\python.exe"
$backendArgs = "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
$frontendCmd  = "frontend\.venv\Scripts\python.exe"
$frontendArgs = "-m streamlit run ui\app.py --server.port 8501 --server.headless true"

# 3) Lanzar procesos
Write-Host "Iniciando backend (FastAPI)..." -ForegroundColor Cyan
$backend = Start-Process -FilePath $backendCmd -ArgumentList $backendArgs -PassThru -WindowStyle Hidden

Start-Sleep -Seconds 2

Write-Host "Iniciando frontend (Streamlit)..." -ForegroundColor Cyan
$frontend = Start-Process -FilePath $frontendCmd -ArgumentList $frontendArgs -PassThru -WindowStyle Hidden

Write-Host ""
Write-Host "Backend  -> http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend -> http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "Backend PID:  $($backend.Id)"
Write-Host "Frontend PID: $($frontend.Id)"
Write-Host ""
Write-Host "Presiona ENTER para detener ambos servicios..." -ForegroundColor Yellow

[void][System.Console]::ReadLine()

# 4) Detener procesos
Write-Host "Deteniendo servicios..." -ForegroundColor Cyan
try { Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue } catch {}
try { Stop-Process -Id $backend.Id  -Force -ErrorAction SilentlyContinue } catch {}

Write-Host "Listo. Servicios detenidos." -ForegroundColor Green
