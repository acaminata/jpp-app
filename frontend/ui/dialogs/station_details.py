# frontend/ui/dialogs/station_details.py
from __future__ import annotations
import pandas as pd
import streamlit as st
from typing import Dict
from ..services.data import fetch_telemetry_summary
from ..utils.formatting import fmt_num
from ..utils.assets import load_asset_text

@st.dialog("Detalles de estación", width="large")
def show_station_dialog(station: Dict):
    """Diálogo: muestra KPIs y tabla por producto/tanque para una estación."""
    # 1) Inyectar CSS global del diálogo
    st.markdown(f"<style>{load_asset_text('styles', 'dialog.css')}</style>", unsafe_allow_html=True)

    # 2) Encabezado
    cid = int(station.get("client_id") or 0)
    sname = station.get("client_description") or str(cid)
    st.caption(f"**Estación:** {cid} – {sname}")
    st.write("")

    # 3) Datos de backend
    with st.spinner("Obteniendo capacidades y lecturas…"):
        try:
            data = fetch_telemetry_summary(cid)
        except Exception as e:
            st.error(f"No se pudo cargar la telemetría: {e}")
            return

    products = (data or {}).get("products", [])
    if not products:
        st.info("No se encontraron tanques/productos para esta estación.")
        return

    # 4) Render por filas de hasta 4 columnas
    max_cols = min(4, len(products)) if products else 1

    def rows(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i+n]

    kpi_tpl = load_asset_text("templates", "kpi_grid.html")

    for row in rows(products, max_cols):
        cols = st.columns(max_cols, gap="small")
        for i, p in enumerate(row):
            with cols[i]:
                with st.container(border=True):
                    pname       = p.get("product_name") or "—"
                    tanks_count = int(p.get("tanks_count") or 0)
                    cap_m3      = p.get("capacity_m3")
                    init_m3     = p.get("initial_product_m3")
                    tanks       = p.get("tanks") or []

                    st.subheader(pname)

                    # KPIs alineados (3 columnas)
                    st.markdown(
                        kpi_tpl.format(
                            cap=fmt_num(cap_m3, 0),
                            stock=fmt_num(init_m3, 2),
                            tks=tanks_count
                        ),
                        unsafe_allow_html=True
                    )

                    # Tabla por tanque (ajustada al contenido con st.table)
                    if tanks:
                        tdf = pd.DataFrame(tanks).rename(columns={
                            "capacity_m3": "Cap.",
                            "initial_volume_m3": "Stock ini."
                        })
                        # Sólo las columnas que quieres ver
                        tdf = tdf[[c for c in ["Cap.", "Stock ini."] if c in tdf.columns]].copy()

                        # Asegura tipos numéricos
                        if "Cap." in tdf: tdf["Cap."] = pd.to_numeric(tdf["Cap."], errors="coerce")
                        if "Stock ini." in tdf: tdf["Stock ini."] = pd.to_numeric(tdf["Stock ini."], errors="coerce")

                        st.dataframe(
                            tdf,
                            use_container_width=True,
                            hide_index=True,  # ← sin índice
                            column_config={
                                "Cap.": st.column_config.NumberColumn("Cap.", width="small", format="%.0f"),
                                "Stock ini.": st.column_config.NumberColumn("Stock ini.", width="small", format="%.2f"),
                            },
                        )
                    else:
                        st.caption("Sin detalle de tanques.")

