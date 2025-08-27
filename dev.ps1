# dev.ps1 (robusto)
$ErrorActionPreference = "Stop"

# --- Paths base
$Root        = Split-Path -Parent $PSCommandPath
$BackendDir  = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"

$BackendPy  = Join-Path $BackendDir  ".venv\Scripts\python.exe"
$FrontendPy = Join-Path $FrontendDir ".venv\Scripts\python.exe"

# --- Logs
$Logs = Join-Path $Root ".logs"
if (!(Test-Path $Logs)) { New-Item -ItemType Directory -Path $Logs | Out-Null }

# --- Comprobaciones previas
if (!(Test-Path $BackendPy))  { throw "No existe $BackendPy (¿creaste el venv de backend?)." }
if (!(Test-Path $FrontendPy)) { throw "No existe $FrontendPy (¿creaste el venv de frontend?)." }

# Paquetes mínimos
& $BackendPy -m pip show uvicorn   | Out-Null 2>&1
if ($LASTEXITCODE -ne 0) { throw "uvicorn no está instalado en el venv de backend." }

& $FrontendPy -m pip show streamlit | Out-Null 2>&1
if ($LASTEXITCODE -ne 0) { throw "streamlit no está instalado en el venv de frontend." }

# --- Cargar backend\.env al entorno (fallback robusto)
$EnvFile = Join-Path $BackendDir ".env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match "^\s*#") { return }
        if ($_ -match "^\s*$") { return }
        $parts = $_.Split("=",2)
        if ($parts.Count -eq 2) {
            $name  = $parts[0].Trim()
            $value = $parts[1].Trim()
            [System.Environment]::SetEnvironmentVariable($name, $value)
        }
    }
} else {
    Write-Warning "No se encontró backend\.env. Recuerda copiar .env.sample a .env"
}

# --- Variables de entorno para el frontend
# Si frontend no usa secrets.toml, tomará estos valores vía os.getenv() (recomendado para dev)
if (-not $env:BACKEND_URL) { $env:BACKEND_URL = "http://localhost:8000" }

# Si no quedó seteado desde .env, usa un valor por defecto de dev (no pisa si ya vino de .env)
if (-not $env:API_KEY) { $env:API_KEY = "dev-secret-key" }

# --- (Opcional) Autocrear secrets.toml local si no existe para st.secrets
$SecretsDir  = Join-Path $FrontendDir ".streamlit"
$SecretsFile = Join-Path $SecretsDir "secrets.toml"
if (!(Test-Path $SecretsFile)) {
    if (!(Test-Path $SecretsDir)) { New-Item -ItemType Directory -Path $SecretsDir | Out-Null }
@"
BACKEND_URL = "http://localhost:8000"
API_KEY = "$($env:API_KEY)"
"@ | Set-Content $SecretsFile -Encoding UTF8
    Write-Host "Creado $SecretsFile" -ForegroundColor Yellow
}

# --- Verificar puertos
$portsBusy = Get-NetTCPConnection -LocalPort 8000,8501 -State Listen -ErrorAction SilentlyContinue
if ($portsBusy) {
    $list = $portsBusy | Select-Object -ExpandProperty LocalPort -Unique | Sort-Object | ForEach-Object { $_ } | Out-String
    throw "Hay puertos ocupados: $list`nCierra procesos o cambia los puertos."
}

# --- Comandos
$BackendArgs  = "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
$FrontendArgs = "-m streamlit run ui\app.py --server.port 8501 --server.headless true"

# --- Lanzar backend con working dir correcto y logs
$BackendOut = Join-Path $Logs "backend.out.log"
$BackendErr = Join-Path $Logs "backend.err.log"
Write-Host "Iniciando backend (FastAPI)..." -ForegroundColor Cyan
$backend = Start-Process -FilePath $BackendPy `
    -ArgumentList $BackendArgs `
    -WorkingDirectory $BackendDir `
    -RedirectStandardOutput $BackendOut `
    -RedirectStandardError  $BackendErr `
    -PassThru

Start-Sleep -Seconds 2

# Chequeo rápido de vida
if ($backend.HasExited) {
    Write-Host "Backend salió inmediatamente. Revisa logs:" -ForegroundColor Red
    Write-Host "  $BackendOut"
    Write-Host "  $BackendErr"
    throw "No se pudo iniciar el backend."
}

# --- Lanzar frontend con working dir correcto y logs
$FrontendOut = Join-Path $Logs "frontend.out.log"
$FrontendErr = Join-Path $Logs "frontend.err.log"
Write-Host "Iniciando frontend (Streamlit)..." -ForegroundColor Cyan
$frontend = Start-Process -FilePath $FrontendPy `
    -ArgumentList $FrontendArgs `
    -WorkingDirectory $FrontendDir `
    -RedirectStandardOutput $FrontendOut `
    -RedirectStandardError  $FrontendErr `
    -PassThru

Start-Sleep -Seconds 2

if ($frontend.HasExited) {
    Write-Host "Frontend salió inmediatamente. Revisa logs:" -ForegroundColor Red
    Write-Host "  $FrontendOut"
    Write-Host "  $FrontendErr"
    # Cerrar backend si frontend falló
    try { Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue } catch {}
    throw "No se pudo iniciar el frontend."
}

Write-Host ""
Write-Host "Backend  -> http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend -> http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "Backend PID:  $($backend.Id)"
Write-Host "Frontend PID: $($frontend.Id)"
Write-Host ""
Write-Host "Logs en: $Logs"
Write-Host "Presiona ENTER para detener ambos servicios..." -ForegroundColor Yellow
[void][System.Console]::ReadLine()

Write-Host "Deteniendo servicios..." -ForegroundColor Cyan
try { Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue } catch {}
try { Stop-Process -Id $backend.Id  -Force -ErrorAction SilentlyContinue } catch {}
Write-Host "Listo. Servicios detenidos." -ForegroundColor Green
