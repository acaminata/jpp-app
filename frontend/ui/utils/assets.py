# frontend/ui/utils/assets.py
from __future__ import annotations
import os

def load_asset_text(*relative_path: str) -> str:
    """Lee un asset de texto (CSS/HTML) bajo ui/assets/* y retorna su contenido."""
    base = os.path.join("ui", "assets")
    full = os.path.join(base, *relative_path)
    with open(full, "r", encoding="utf-8") as f:
        return f.read()
