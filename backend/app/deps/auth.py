import os
from fastapi import Header, HTTPException, status

API_KEY = os.getenv("API_KEY", "")

async def require_api_key(x_api_key: str | None = Header(None)):
    if not API_KEY:  # si no configuraste la variable en Render
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="API not configured")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
