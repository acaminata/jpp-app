# frontend/ui/components/station_card.py
from __future__ import annotations
import streamlit as st
from typing import Dict
from ..dialogs.station_details import show_station_dialog

def render_station_card(col, station: Dict, idx: int) -> None:
    """Tarjeta de estación con botón 'Ver detalles' que abre el diálogo."""
    title = str(station.get("client_id") or "—")
    subtitle = station.get("client_description") or "Razón social no informada"
    zone = station.get("zone_name") or station.get("zone_id") or "Zona no especificada"
    boss = station.get("zone_manager_name")

    try:
        with col.container(border=True):
            st.markdown(f"### {title}")
            st.caption(subtitle)
            st.write(zone)
            if boss:
                st.write(f"**Jefe de zona:** {boss}")
            if st.button("Ver detalles", key=f"details_{title}_{idx}", use_container_width=True):
                show_station_dialog(station)
    except TypeError:
        with col.container():
            st.markdown("---")
            st.markdown(f"### {title}")
            st.caption(subtitle)
            st.write(zone)
            if boss:
                st.write(f"**Jefe de zona:** {boss}")
            if st.button("Ver detalles", key=f"details_{title}_{idx}", use_container_width=True):
                show_station_dialog(station)
