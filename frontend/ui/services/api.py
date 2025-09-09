# frontend/ui/services/api.py
from __future__ import annotations
import os, time, requests, streamlit as st
from typing import Any, Dict, Optional

# Configuración de backend (secrets/env)
BACKEND_URL: str = st.secrets.get("BACKEND_URL", os.getenv("BACKEND_URL", "http://localhost:8000"))
API_KEY: Optional[str] = st.secrets.get("API_KEY", os.getenv("API_KEY"))

def api_get(path: str, params: Optional[Dict[str, Any]] = None, retries: int = 2, timeout: int = 30) -> requests.Response:
    """GET con reintentos y header de API Key."""
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    url = f"{BACKEND_URL.rstrip('/')}/{path.lstrip('/')}"
    for i in range(retries + 1):
        try:
            return requests.get(url, params=params, headers=headers, timeout=timeout)
        except requests.exceptions.RequestException:
            if i == retries:
                raise
            time.sleep(1 + i)
