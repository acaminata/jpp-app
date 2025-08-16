import os
import requests
import pandas as pd
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
st.set_page_config(page_title="JPP – Planificador", page_icon="⛽", layout="centered")

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
- En el siguiente paso, seleccionar EDS, configurar restricciones y ejecutar la optimización.
""")

st.divider()
st.markdown("### 1) Selecciona una planta")

@st.cache_data(show_spinner=True)
def fetch_plants():
    r = requests.get(f"{BACKEND_URL}/plants", timeout=30)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    # Asegura columnas esperadas por si acaso
    df = df.rename(columns={
        "werksreal": "plant_id",
        "name1werksreal": "plant_name",
        "id": "plant_id",
        "name": "plant_name",
    })
    return df

try:
    df = fetch_plants()
    if df.empty or "plant_id" not in df.columns:
        st.warning("No se encontraron plantas o el formato no es el esperado.")
    else:
        def fmt_label(row):
            pid = int(row["plant_id"]) if pd.notnull(row["plant_id"]) else "—"
            pname = row["plant_name"] if ("plant_name" in row and pd.notnull(row["plant_name"])) else ""
            return f"{pid} – {pname}".strip(" –")

        df["label"] = df.apply(fmt_label, axis=1)

        selection = st.selectbox("Planta", df["label"].tolist())
        selected_row = df.loc[df["label"] == selection].iloc[0]
        selected_plant_id = int(selected_row["plant_id"])
        st.success(f"Planta seleccionada: **{selected_plant_id}**")
        st.session_state["selected_plant_id"] = selected_plant_id
except Exception as e:
    st.error(f"Error al cargar plantas: {e}")
