# ---- imports ----
import os
import requests
import pandas as pd
import streamlit as st
from urllib.parse import quote_plus

# ---- config ----
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
st.set_page_config(page_title="JPP – Planificador", page_icon="⛽", layout="wide")

# ---- encabezado ----
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

# ---- data helpers ----
@st.cache_data(show_spinner=True)
def fetch_plants():
    r = requests.get(f"{BACKEND_URL}/plants", timeout=30)
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
    r = requests.get(f"{BACKEND_URL}/plant-stations", params={"plant_id": plant_id}, timeout=60)
    r.raise_for_status()
    return r.json()

def _fmt_plant_label(row) -> str:
    pid = int(row["plant_id"]) if pd.notnull(row.get("plant_id")) else "—"
    pname = row.get("plant_name")
    return f"{pid} – {pname}" if pd.notnull(pname) else f"{pid}"

def _google_query_url(client_description: str | None, zone_name: str | None):
    if not client_description:
        return None
    q = f"{client_description} {zone_name} Copec" if zone_name else f"{client_description} Copec"
    return f"https://www.google.com/search?q={quote_plus(q)}"

def _render_station_card(col, station: dict):
    # Título: código estación (client_id)
    title = str(station.get("client_id") or "—")
    # Subtítulo: razón social
    subtitle = station.get("client_description") or "Razón social no informada"
    # Comuna/zona
    zone = station.get("zone_name") or station.get("zone_id") or "Zona no especificada"
    # Jefe de zona (si viene)
    jefe = station.get("zone_manager_name")
    # Google
    g_url = _google_query_url(station.get("client_description"), station.get("zone_name"))

    try:
        with col.container(border=True):
            st.markdown(f"### {title}")
            st.caption(subtitle)
            st.write(zone)
            if jefe:
                st.write(f"**Jefe de zona:** {jefe}")
            if g_url:
                try:
                    st.link_button("Googlearlo", g_url, use_container_width=True)
                except Exception:
                    st.markdown(f"[Googlearlo]({g_url})")
    except TypeError:
        with col.container():
            st.markdown("---")
            st.markdown(f"### {title}")
            st.caption(subtitle)
            st.write(zone)
            if jefe:
                st.write(f"**Jefe de zona:** {jefe}")
            if g_url:
                st.markdown(f"[Googlearlo]({g_url})")

# ---- selector de planta ----
try:
    df_plants = fetch_plants()
    if df_plants.empty or "plant_id" not in df_plants.columns:
        st.warning("No se encontraron plantas o el formato no es el esperado.")
        st.stop()
    df_plants["label"] = df_plants.apply(_fmt_plant_label, axis=1)
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

# ---- carga estaciones ----
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

# ---- KPIs ----
kpi_cols = st.columns(3)
with kpi_cols[0]:
    st.metric("Total clientes", int(sdf["client_id"].nunique()) if "client_id" in sdf else 0)
with kpi_cols[1]:
    total_zonas = int(sdf["zone_name"].nunique()) if "zone_name" in sdf else int(sdf["zone_id"].nunique())
    st.metric("Total zonas", total_zonas)
with kpi_cols[2]:
    st.metric("Planta", str(selected_plant_name or selected_plant_id))

st.write("")

# ---- buscador ----
search = st.text_input("Filtrar por estación (código), razón social o comuna", value="").strip().lower()

def _match_filter(rec: dict, needle: str) -> bool:
    a = str(rec.get("client_description") or "").lower()
    b = str(rec.get("zone_name") or "").lower()
    c = str(rec.get("client_id") or "").lower()
    return (needle in a) or (needle in b) or (needle in c)

filtered = [r for r in stations if _match_filter(r, search)] if search else stations

# Ordenación: por código estación y luego razón social
filtered = sorted(
    filtered,
    key=lambda r: (int(r.get("client_id") or 0), str(r.get("client_description") or "").lower())
)

# ---- grid de tarjetas ----
n_cols = 3
cols = st.columns(n_cols)
for i, stn in enumerate(filtered):
    _render_station_card(cols[i % n_cols], stn)
