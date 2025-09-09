# ui/utils/assets.py
from __future__ import annotations
from pathlib import Path

# Directorio 'ui' (dos niveles arriba de este archivo: ui/utils/assets.py)
_UI_DIR = Path(__file__).resolve().parents[1]
_ASSETS_DIR = _UI_DIR / "assets"

def load_asset_text(*relative_path: str) -> str:
    """
    Lee un asset de texto (CSS/HTML) bajo ui/assets/* de forma robusta,
    independiente del working directory (local o Streamlit Cloud).
    """
    primary = _ASSETS_DIR.joinpath(*relative_path)

    # Fallback por si el runtime parte en el repo root (frontend/ui/...)
    alt = Path.cwd() / "frontend" / "ui" / "assets" / Path(*relative_path)

    if primary.exists():
        return primary.read_text(encoding="utf-8")
    if alt.exists():
        return alt.read_text(encoding="utf-8")

    raise FileNotFoundError(
        f"No se encontró el asset: {primary} (fallback probado: {alt})"
    )
