# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import plants, stations  # <- añade stations

app = FastAPI(title="JPP Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_allowed_origins] if settings.cors_allowed_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

# Routers registrados
app.include_router(plants.router)
app.include_router(stations.router)  # <- nuevo include
