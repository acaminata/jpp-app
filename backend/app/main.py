# backend/app/main.py
from fastapi import FastAPI, Depends  # <- añade Depends
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import plants, stations, telemetry, demand
from .deps.auth import require_api_key

app = FastAPI(title="JPP Backend", version="0.1.0", docs_url=None, redoc_url=None)

# Ajuste CORS: si usas "*", no permitas credentials
allow_origins = (
    ["*"] if settings.cors_allowed_origins in ("", "*") else [settings.cors_allowed_origins]
)
allow_credentials = False if "*" in allow_origins else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", dependencies=[Depends(require_api_key)])  # protege /health (opcional)
def health():
    return {"ok": True}

# protege routers completos
app.include_router(plants.router, dependencies=[Depends(require_api_key)])
app.include_router(stations.router, dependencies=[Depends(require_api_key)])
app.include_router(telemetry.router, dependencies=[Depends(require_api_key)]) 
app.include_router(demand.router, dependencies=[Depends(require_api_key)])