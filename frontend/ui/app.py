import os
import requests
import pandas as pd
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="JPP – Planificador", page_icon="⛽", layout="centered")

# Header
col_logo, col_title = st.columns([1, 3], gap="large")
with col_logo:
    st.image("ui/assets/copec_logo.png", use_container_width=True)
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
    return pd.DataFrame(r.json())

try:
    df = fetch_plants()
    if df.empty:
        st.warning("No se encontraron plantas.")
    else:
        df["label"] = df.apply(
            lambda r: f"{int(r['werksreal'])} – {r['name1werksreal']}" if pd.notnull(r["name1werksreal"]) else f"{int(r['werksreal'])}",
            axis=1
        )
        selected = st.selectbox("Planta", df["label"].tolist())
        selected_plant = int(df.loc[df["label"] == selected, "werksreal"].iloc[0])
        st.success(f"Planta seleccionada: **{selected_plant}**")
        st.session_state["selected_plant"] = selected_plant
except Exception as e:
    st.error(f"Error al cargar plantas: {e}")

st.divider()
st.markdown("### 2) Próximo paso")
st.write("Agregaremos selección de EDS, parámetros y botón de ejecutar optimización.")