from fastapi import APIRouter, HTTPException, Query
from typing import List
import pandas as pd

from ..deps.athena import get_athena_connection
from ..schemas.station import Station

router = APIRouter(tags=["stations"])

QUERY = """
SELECT DISTINCT
    CAST(e.werksreal AS INTEGER) AS plant_id,
    e.name1werksreal             AS plant_name,
    CAST(e.kunag AS INTEGER)     AS client_id,
    e.name1kunag                 AS client_description,
    e.zone1                      AS zone_id,
    e.vtext                      AS zone_name,
    mjz.znombre_1_key            AS zone_manager_name,
    vm.cod_camion_tipo           AS truck_type
FROM logistica_scr_staging.etlist e
LEFT JOIN venta_concesionario_staging.venta_mensual vm
    ON TRY_CAST(vm.razon_social AS INTEGER) = CAST(e.kunag AS INTEGER)
LEFT JOIN maestros_staging.maestro_jefes_zona mjz
    ON TRY_CAST(vm.cod_zona_jefe AS INTEGER) = TRY_CAST(mjz.sales_grp_key AS INTEGER)
WHERE
    e.auart IN ('ZC01', 'ZCES')
    AND regexp_like(e.werksreal, '^[0-9]+$')
    AND regexp_like(e.kunag, '^[0-9]+$')
    AND CAST(e.werksreal AS INTEGER) = %(plant_id)s
    AND try_cast(e.vdatu AS DATE) >= date_add('month', -3, current_date)
ORDER BY plant_id, client_id
"""

@router.get("/plant-stations", response_model=List[Station])
def list_plant_stations(plant_id: int = Query(..., description="Plant ID (integer)")):
    try:
        with get_athena_connection() as conn:
            df = pd.read_sql(QUERY, conn, params={"plant_id": plant_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Athena query failed: {e}")

    if df is None or df.empty:
        return []

    # Normalización
    for col in (
        "plant_name", "client_description",
        "zone_id", "zone_name", "zone_manager_name", "truck_type"
    ):
        if col in df.columns:
            df[col] = df[col].astype(str).where(df[col].notna(), None)

    for col in ("plant_id", "client_id"):
        if col in df.columns:
            try:
                df[col] = df[col].astype("Int64")
            except Exception:
                pass

    return [Station(**row.to_dict()) for _, row in df.iterrows()]
