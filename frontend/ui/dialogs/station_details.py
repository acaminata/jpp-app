# frontend/ui/dialogs/station_details.py
from __future__ import annotations

from typing import Dict
import pandas as pd
import streamlit as st
import requests
from datetime import timedelta

from services.data import fetch_telemetry_summary, fetch_demand_curve
from utils.formatting import fmt_num
from utils.assets import load_asset_text


@st.dialog("Detalles de estación", width="large")
def show_station_dialog(station: Dict):
    """Diálogo de detalles de una estación (EDS):
       - Inputs y curva de DEMANDA (arriba del diálogo)
       - KPIs y tabla por producto/tanque (TELEMETRÍA)
    """
    # ===== 0) CSS global del diálogo
    try:
        st.markdown(f"<style>{load_asset_text('styles', 'dialog.css')}</style>", unsafe_allow_html=True)
    except Exception:
        # si no existe el asset, seguimos sin bloquear
        pass

    # ===== 1) Encabezado
    cid = int(station.get("client_id") or 0)
    sname = station.get("client_description") or str(cid)
    st.caption(f"**Estación:** {cid} – {sname}")
    st.write("")

    # ---------------------------------------------------------------------
    # SECCIÓN A: DEMANDA (inputs arriba + curva promedio por hora)
    # ---------------------------------------------------------------------
    state_prefix = f"demand_{cid}"

    # 1) Cargar defaults una sola vez
    if f"{state_prefix}_loaded" not in st.session_state:
        try:
            d0 = fetch_demand_curve(cid)  # defaults server-side
        except requests.HTTPError as http_err:
            status = getattr(http_err.response, "status_code", "?")
            url = getattr(http_err.response, "url", "desconocida")
            body = ""
            try:
                body = http_err.response.text[:1000]
            except Exception:
                body = str(http_err)
            st.error(f"Backend {status} en {url}\n\n{body}")
            d0 = None
        except Exception as e:
            st.error(f"No se pudo cargar la curva de demanda inicial: {e}")
            d0 = None

        if d0:
            st.session_state[f"{state_prefix}_start"] = pd.to_datetime(d0.get("start_date")).date()
            st.session_state[f"{state_prefix}_weeks"] = int(d0.get("weeks", 8))
            st.session_state[f"{state_prefix}_end"]   = pd.to_datetime(d0.get("end_date")).date()
            st.session_state[f"{state_prefix}_data"]  = d0
            st.session_state[f"{state_prefix}_data_max"] = pd.to_datetime(d0.get("data_max_date")).date()
        else:
            today = pd.Timestamp.today().date()
            st.session_state[f"{state_prefix}_start"] = today
            st.session_state[f"{state_prefix}_weeks"] = 8
            st.session_state[f"{state_prefix}_end"]   = (today + pd.Timedelta(weeks=8) - pd.Timedelta(days=1))
            st.session_state[f"{state_prefix}_data"]  = None
            st.session_state[f"{state_prefix}_data_max"] = today

        st.session_state[f"{state_prefix}_loaded"] = True

    # 2) Inputs arriba (con límites dinámicos)
    today = pd.Timestamp.today().date()
    data_max = st.session_state[f"{state_prefix}_data_max"]

    # semanas máximas a partir de hoy para no superar data_max
    def _global_max_weeks(today_date, max_date):
        days = (max_date - today_date).days + 1
        return max(1, days // 7)

    # límite superior del inicio según weeks elegido: start_max = data_max - (weeks*7 - 1)
    def _start_max_for(weeks_val: int):
        # asegura entero y no negativo
        w = max(1, int(weeks_val))
        # usa datetime.timedelta para operar sobre date
        return data_max - timedelta(days=w * 7 - 1)

    # Renderizamos primero "Semanas" para poder fijar max del inicio
    c1, c2, c3 = st.columns([1.0, 1.2, 1.2])

    with c1:
        global_weeks_cap = int(_global_max_weeks(today, data_max))
        weeks_input = st.number_input(
            "Semanas de simulación",
            min_value=1,
            max_value=global_weeks_cap,
            value=min(int(st.session_state[f"{state_prefix}_weeks"]), global_weeks_cap),
            step=1,
            key=f"{state_prefix}_weeks_input",
        )

    # Ahora podemos calcular el máximo permitido del inicio para estas weeks
    start_max_allowed = _start_max_for(int(weeks_input))
    # Evitar que max < min en date_input
    if start_max_allowed < today:
        start_max_allowed = today

    with c2:
        start_input = st.date_input(
            "Inicio del período",
            st.session_state[f"{state_prefix}_start"],
            min_value=today,                # no pasado
            max_value=start_max_allowed,    # no llevar el fin más allá de data_max
            format="DD-MM-YYYY",
            key=f"{state_prefix}_start_input",
        )

    # Fin auto local
    computed_end = (pd.to_datetime(start_input).date()
                    + timedelta(weeks=int(weeks_input))
                    - timedelta(days=1))
    # Clamp visual al data_max, por si el borde cae en el mismo día
    computed_end_display = min(computed_end, data_max)

    with c3:
        st.text_input(
            "Fin del período (auto)",
            value=computed_end_display.strftime("%d-%m-%Y"),
            disabled=True,
        )

    # 3) Validaciones & re-fetch
    if start_input < today:
        st.error("La fecha de inicio no puede ser en el pasado.")
    elif computed_end > data_max:
        st.warning(
            f"El período propuesto excede la última fecha disponible ({data_max.strftime('%d-%m-%Y')}). "
            "Ajusta inicio o semanas."
        )
    else:
        if (
            start_input != st.session_state[f"{state_prefix}_start"] or
            int(weeks_input) != st.session_state[f"{state_prefix}_weeks"]
        ):
            try:
                dnew = fetch_demand_curve(cid, start_date=start_input.isoformat(), weeks=int(weeks_input))
                st.session_state[f"{state_prefix}_data"]   = dnew
                st.session_state[f"{state_prefix}_start"]  = pd.to_datetime(dnew.get("start_date")).date()
                st.session_state[f"{state_prefix}_weeks"]  = int(dnew.get("weeks", weeks_input))
                st.session_state[f"{state_prefix}_end"]    = pd.to_datetime(dnew.get("end_date")).date()
                st.session_state[f"{state_prefix}_data_max"] = pd.to_datetime(dnew.get("data_max_date")).date()
                data_max = st.session_state[f"{state_prefix}_data_max"]  # refresca para la UI
            except requests.HTTPError as e:
                msg = getattr(e.response, "text", str(e))
                st.error(f"No se pudo recalcular la curva: {msg}")
            except Exception as e:
                st.error(f"No se pudo recalcular la curva: {e}")

    demand = st.session_state.get(f"{state_prefix}_data")

    # 4) Gráfico (sólo productos con datos) y X 0..23
    if demand:
        curves = demand.get("curves", [])
        total = demand.get("total_hourly_m3", [0.0] * 24)

        curves_nonzero = []
        for c in curves:
            arr = c.get("hourly_m3") or []
            if any((v or 0) > 0 for v in arr):
                curves_nonzero.append(c)

        df_lines = pd.DataFrame({"Hora": list(range(24))}).set_index("Hora")
        for c in curves_nonzero:
            df_lines[c["product_name"]] = (c["hourly_m3"] or [0.0]*24)[:24]
        df_lines["Total"] = (total or [0.0]*24)[:24]

        import altair as alt
        df_long = df_lines.reset_index().melt("Hora", var_name="Producto", value_name="m3")

        chart = (
            alt.Chart(df_long)
            .mark_line()
            .encode(
                x=alt.X("Hora:Q", scale=alt.Scale(domain=[0, 23]), axis=alt.Axis(values=list(range(0, 24)))),
                y=alt.Y("m3:Q", title="m³"),
                color=alt.Color("Producto:N", legend=alt.Legend(title="Producto"))
            )
            .properties(height=260)
            .interactive(bind_y=False)
        )

        st.markdown("#### Curva promedio por hora (m³)")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No hay datos de demanda disponibles para este período.")

    st.divider()

    # ---------------------------------------------------------------------
    # SECCIÓN B: TELEMETRÍA (KPIs por producto + tabla por tanque)
    # ---------------------------------------------------------------------
    with st.spinner("Obteniendo capacidades y lecturas…"):
        try:
            data = fetch_telemetry_summary(cid)
        except requests.HTTPError as http_err:
            status = getattr(http_err.response, "status_code", "?")
            url = getattr(http_err.response, "url", "desconocida")
            body = ""
            try:
                body = http_err.response.text[:1000]
            except Exception:
                body = str(http_err)
            st.error(f"Backend {status} en {url}\n\n{body}")
            return
        except Exception as e:
            st.error(f"No se pudo cargar la telemetría: {e}")
            return

    products = (data or {}).get("products", [])
    if not products:
        st.info("No se encontraron tanques/productos para esta estación.")
        return

    # Grid responsivo: hasta 4 columnas por fila
    max_cols = min(4, len(products)) if products else 1

    def _rows(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i : i + n]

    kpi_tpl = ""
    try:
        kpi_tpl = load_asset_text("templates", "kpi_grid.html")
    except Exception:
        # fallback simplificado si no existiera la plantilla
        kpi_tpl = (
            "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:8px;'>"
            "<div><div style='font-size:12px;color:#5f6b7a;'>Capacidad (m³)</div><div style='font-weight:700;'>{cap}</div></div>"
            "<div><div style='font-size:12px;color:#5f6b7a;'>Lectura inicial (m³)</div><div style='font-weight:700;'>{stock}</div></div>"
            "<div><div style='font-size:12px;color:#5f6b7a;'>Tanques</div><div style='font-weight:700;'>{tks}</div></div>"
            "</div>"
        )

    for row in _rows(products, max_cols):
        cols = st.columns(len(row), gap="small")
        for i, p in enumerate(row):
            with cols[i]:
                with st.container(border=True):
                    pname = p.get("product_name") or "—"
                    tanks_count = int(p.get("tanks_count") or 0)
                    cap_m3 = p.get("capacity_m3")
                    init_m3 = p.get("initial_product_m3")
                    tanks = p.get("tanks") or []

                    st.subheader(pname)

                    # KPIs
                    st.markdown(
                        kpi_tpl.format(
                            cap=fmt_num(cap_m3, 0),
                            stock=fmt_num(init_m3, 2),
                            tks=tanks_count,
                        ),
                        unsafe_allow_html=True,
                    )

                    # Tabla por tanque
                    if tanks:
                        tdf = pd.DataFrame(tanks).rename(
                            columns={
                                "tank_id": "Tanque",
                                "capacity_m3": "Cap.",
                                "initial_volume_m3": "Stock ini.",
                            }
                        )

                        show_cols = [c for c in ["Tanque", "Cap.", "Stock ini."] if c in tdf.columns]
                        tdf = tdf[show_cols].copy()

                        # Tipos numéricos
                        if "Cap." in tdf:
                            tdf["Cap."] = pd.to_numeric(tdf["Cap."], errors="coerce")
                        if "Stock ini." in tdf:
                            tdf["Stock ini."] = pd.to_numeric(tdf["Stock ini."], errors="coerce")

                        st.dataframe(
                            tdf,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Tanque": st.column_config.NumberColumn("Tanque", width="small", format="%d"),
                                "Cap.": st.column_config.NumberColumn("Cap.", width="small", format="%.0f"),
                                "Stock ini.": st.column_config.NumberColumn("Stock ini.", width="small", format="%.2f"),
                            },
                        )
                    else:
                        st.caption("Sin detalle de tanques.")
