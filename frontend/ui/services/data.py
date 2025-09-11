# frontend/ui/services/data.py
from __future__ import annotations
import pandas as pd
import streamlit as st
from .api import api_get

@st.cache_data(show_spinner=True)
def fetch_plants() -> pd.DataFrame:
    """Obtiene la lista de plantas desde el backend."""
    r = api_get("plants", timeout=30)
    r.raise_for_status()
    df = pd.DataFrame(r.json()).rename(columns={
        "werksreal": "plant_id",
        "name1werksreal": "plant_name",
        "id": "plant_id",
        "name": "plant_name",
    })
    if "plant_name" in df.columns:
        df = df.sort_values(by=["plant_name", "plant_id"], na_position="last", kind="mergesort")
    return df.reset_index(drop=True)

@st.cache_data(show_spinner=True)
def fetch_stations(plant_id: int):
    """Retorna estaciones asociadas a la planta (últimos 3 meses)."""
    r = api_get("plant-stations", params={"plant_id": plant_id}, timeout=60)
    r.raise_for_status()
    return r.json()

@st.cache_data(show_spinner=True)
def fetch_telemetry_summary(client_id: int):
    """Resumen de telemetría por estación (capacidades, stock inicial y tanques)."""
    r = api_get("telemetry/summary", params={"client_id": client_id}, timeout=60)
    r.raise_for_status()
    return r.json()

@st.cache_data(show_spinner=True)
def fetch_demand_curve(client_id: int, start_date: str | None = None, weeks: int = 8):
    params = {"client_id": client_id, "weeks": weeks}
    if start_date:
        params["start_date"] = start_date
    r = api_get("demand/curve", params=params, timeout=60)
    r.raise_for_status()
    return r.json()
