from fastapi import APIRouter, HTTPException, Query
from datetime import date, datetime, timedelta
import pandas as pd

from ..deps.athena import get_athena_connection
from ..schemas.demand import DemandCurveResponse, HourlyCurve

router = APIRouter(prefix="/demand", tags=["demand"])

# Mapeo de producto (coincide con telemetría)
PRODUCT_MAP = {
    7: "Kerosene",
    6: "Gasolina 97",
    4: "Gasolina 93",
    5: "Gasolina 95",
    1: "Petróleo Diésel",
}
PRODUCT_ORDER = [7, 6, 4, 5, 1]  # orden de salida

def _next_anchor_start(today: date) -> date:
    """
    Regla default:
    - Ancla = próximo día 1 o 15 (>= hoy)
    - Inicio = primer LUNES >= ancla
    """
    # próximo ancla (1 o 15)
    if today.day <= 1:
        anchor = date(today.year, today.month, 1)
    elif today.day <= 15:
        anchor = date(today.year, today.month, 15)
    else:
        # siguiente mes, día 1
        y = today.year + (1 if today.month == 12 else 0)
        m = 1 if today.month == 12 else today.month + 1
        anchor = date(y, m, 1)

    # primer lunes >= anchor (Lun=0..Dom=6)
    dow = anchor.weekday()
    delta = (0 - dow) % 7
    start = anchor + timedelta(days=delta)
    return start

QUERY = """
SELECT
  CAST(estacion AS INTEGER)   AS client_id,
  CAST(producto AS INTEGER)   AS product_id,
  CAST(volumen AS DOUBLE)     AS volumen_liters,
  fecha                       AS ts
FROM modelos_analytics.prediccion_demanda_eds_resultados
WHERE CAST(estacion AS INTEGER) = %(client_id)s
  AND CAST(producto AS INTEGER) IN (1,4,5,6,7)
  AND fecha BETWEEN DATE(%(start)s) AND DATE(%(end)s)
"""

QUERY_MAX = """
SELECT date(max(fecha)) AS max_date
FROM modelos_analytics.prediccion_demanda_eds_resultados
WHERE CAST(estacion AS INTEGER) = %(client_id)s
  AND CAST(producto AS INTEGER) IN (1,4,5,6,7)
"""

@router.get("/curve", response_model=DemandCurveResponse)
def demand_curve(
    client_id: int = Query(..., description="Código EDS"),
    start_date: date | None = Query(None, description="YYYY-MM-DD (opcional)"),
    weeks: int = Query(8, ge=1, le=26, description="Semanas de simulación (default 8)")
):
    # Fechas por defecto según regla
    today = date.today()
    start = start_date or _next_anchor_start(today)
    end = start + timedelta(weeks=weeks)  # ventana [start, end)
    # end_date de respuesta = domingo anterior a end
    end_resp = end - timedelta(days=1)

    # Ejecutar query
    try:
        with get_athena_connection() as conn:
            df_max = pd.read_sql(QUERY_MAX, conn, params={"client_id": int(client_id)})
            if df_max is None or df_max.empty or pd.isna(df_max.loc[0, "max_date"]):
                # sin datos para esta estación -> respuesta vacía con metadatos
                return DemandCurveResponse(
                    client_id=client_id,
                    start_date=start,
                    end_date=end - timedelta(days=1),
                    weeks=weeks,
                    data_max_date=start,   # o date.today()
                    curves=[],
                    total_hourly_m3=[0.0]*24
                )
            data_max_date = pd.to_datetime(df_max.loc[0, "max_date"]).date()
            
            df = pd.read_sql(
                QUERY, conn,
                params={
                    "client_id": int(client_id),
                    "start": start.isoformat(),
                    "end":   end.isoformat(),
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Athena query failed: {e}")

    if df is None or df.empty:
        # Respuesta vacía pero con metadatos útiles
        return DemandCurveResponse(
            client_id=client_id,
            start_date=start,
            end_date=end_resp,
            weeks=weeks,
            data_max_date=data_max_date, 
            curves=[],
            total_hourly_m3=[0.0]*24
        )

    # Discretizar (redondeo sin decimales) y pasar a m3
    df["volumen_rounded_liters"] = df["volumen_liters"].round(0)
    df["volumen_m3"] = df["volumen_rounded_liters"] / 1000.0

    # Hora del día
    df["hour"] = pd.to_datetime(df["ts"]).dt.hour

    # Promedio por hora y producto
    g = df.groupby(["product_id", "hour"], as_index=False)["volumen_m3"].mean()

    # Construir curvas por producto (24 puntos)
    curves: list[HourlyCurve] = []
    for pid in PRODUCT_ORDER:
        pname = PRODUCT_MAP[pid]
        sub = g[g["product_id"] == pid]
        arr = [0.0]*24
        for _, row in sub.iterrows():
            h = int(row["hour"])
            arr[h] = float(round(row["volumen_m3"], 6))
        curves.append(HourlyCurve(product_name=pname, hourly_m3=arr))

    # Curva total (suma por hora)
    total = [0.0]*24
    for h in range(24):
        total[h] = float(round(sum(c.hourly_m3[h] for c in curves), 6))

    return DemandCurveResponse(
        client_id=client_id,
        start_date=start,
        end_date=end_resp,
        weeks=weeks,
        data_max_date=data_max_date, 
        curves=curves,
        total_hourly_m3=total
    )
