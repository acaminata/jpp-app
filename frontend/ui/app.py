# frontend/ui/app.py
from __future__ import annotations
import os
import pandas as pd
import streamlit as st
from services.data import fetch_plants, fetch_stations
from utils.formatting import fmt_plant_label
from components.station_card import render_station_card

# Configuración de página
st.set_page_config(page_title="JPP – Planificador", page_icon="⛽", layout="wide")

# Encabezado
col_logo, col_title = st.columns([1, 3], gap="large")
with col_logo:
    logo_path = os.path.join("ui", "assets", "copec_logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_column_width=True)
with col_title:
    st.title("JPP")
    st.subheader("Optimizador de programación de pedidos de combustibles")

st.markdown("""
Bienvenida/o a **JPP App**. Este prototipo permite:
- Consultar **plantas** disponibles desde Athena (vía API).
- Seleccionar EDS, ver clientes asociados y, en siguientes pasos, configurar restricciones y ejecutar la optimización.
""")

st.divider()
st.markdown("### 1) Selecciona una planta")

# Selector de planta
try:
    df_plants = fetch_plants()
    if df_plants.empty or "plant_id" not in df_plants.columns:
        st.warning("No se encontraron plantas o el formato no es el esperado.")
        st.stop()
    df_plants["label"] = df_plants.apply(fmt_plant_label, axis=1)
    selection = st.selectbox("Planta", df_plants["label"].tolist())
    selected_row = df_plants.loc[df_plants["label"] == selection].iloc[0]
    selected_plant_id = int(selected_row["plant_id"])
    selected_plant_name = selected_row.get("plant_name")
    st.success(f"Planta seleccionada: **{selected_plant_id}**")
    st.session_state["selected_plant_id"] = selected_plant_id
except Exception as e:
    st.error(f"Error al cargar plantas: {e}")
    st.stop()

st.divider()
st.markdown("### 2) Clientes/Estaciones asociados a la planta seleccionada (últimos 3 meses)")

# Carga de estaciones
with st.spinner("Cargando estaciones..."):
    try:
        stations = fetch_stations(selected_plant_id)
    except Exception as e:
        st.error(f"No se pudieron cargar las estaciones: {e}")
        st.stop()

if not stations:
    st.info("No se encontraron clientes para los últimos 3 meses.")
    st.stop()

sdf = pd.DataFrame(stations)

# KPIs
k1, k2, k3 = st.columns(3)
with k1:
    st.metric("Total clientes", int(sdf["client_id"].nunique()) if "client_id" in sdf else 0)
with k2:
    total_zonas = int(sdf["zone_name"].nunique()) if "zone_name" in sdf else int(sdf["zone_id"].nunique())
    st.metric("Total zonas", total_zonas)
with k3:
    st.metric("Planta", str(selected_plant_name or selected_plant_id))

st.write("")

# Buscador + grid
search = st.text_input("Filtrar por estación (código), razón social o comuna", value="").strip().lower()

def _match(rec: dict, needle: str) -> bool:
    a = str(rec.get("client_description") or "").lower()
    b = str(rec.get("zone_name") or "").lower()
    c = str(rec.get("client_id") or "").lower()
    return (needle in a) or (needle in b) or (needle in c)

filtered = [r for r in stations if _match(r, search)] if search else stations
filtered = sorted(filtered, key=lambda r: (int(r.get("client_id") or 0), str(r.get("client_description") or "").lower()))

n_cols = 3
cols = st.columns(n_cols)
for i, stn in enumerate(filtered):
    render_station_card(cols[i % n_cols], stn, i)
