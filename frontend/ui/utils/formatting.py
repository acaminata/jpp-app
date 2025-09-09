# frontend/ui/utils/formatting.py
from __future__ import annotations
import pandas as pd
from typing import Any

def fmt_num(x: Any, nd: int = 2) -> str:
    """Formatea número con 'nd' decimales; guion si es nulo."""
    if x is None:
        return "—"
    try:
        return f"{float(x):,.{nd}f}"
    except Exception:
        return str(x)

def fmt_plant_label(row) -> str:
    """Devuelve 'id – nombre' para el selector de planta."""
    pid = int(row["plant_id"]) if pd.notnull(row.get("plant_id")) else "—"
    pname = row.get("plant_name")
    return f"{pid} – {pname}" if pd.notnull(pname) else f"{pid}"
