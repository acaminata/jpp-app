from fastapi import APIRouter, HTTPException, Query
import pandas as pd
import traceback
import logging
from ..deps.athena import get_athena_connection
from ..schemas.telemetry import TelemetrySummary, ProductSummary, TankSummary

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

Q1_TANKS = """
WITH base AS (
  SELECT
    CAST(ubicacioncodigo AS INTEGER)                 AS client_id,
    CAST(tanque           AS INTEGER)                AS tank_id,
    CAST(protucto         AS INTEGER)                AS product_id,
    CAST(capacidad        AS DOUBLE)                 AS capacity_liters,
    from_unixtime(try_cast(telemedicionfecha AS bigint)) AS snap_ts,
    row_number() OVER (
      PARTITION BY ubicacioncodigo, tanque
      ORDER BY try_cast(telemedicionfecha AS bigint) DESC, fecha_envio DESC
    ) AS rn
  FROM copecfuel_staging.telemedicion_detalle
  WHERE CAST(ubicacioncodigo AS INTEGER) = %(client_id)s
    AND protucto IN (1,4,5,6,7)  -- 1=Diésel, 4=93, 5=95, 6=97, 7=Kerosene
    AND from_unixtime(try_cast(telemedicionfecha AS bigint)) >= date_add('hour', -24, current_timestamp)
)
SELECT
  client_id,
  tank_id,
  CASE product_id
    WHEN 7 THEN 'Kerosene'
    WHEN 6 THEN 'Gasolina 97'
    WHEN 4 THEN 'Gasolina 93'
    WHEN 5 THEN 'Gasolina 95'
    WHEN 1 THEN 'Petróleo Diésel'
    ELSE CAST(product_id AS VARCHAR)
  END AS product_name,
  capacity_liters
FROM base
WHERE rn = 1;
"""

Q2_INIT = """
WITH base AS (
  SELECT
    CAST(ubicacioncodigo AS INTEGER)       AS client_id,
    CAST(tanque AS INTEGER)                AS tank_id,
    CAST(protucto AS INTEGER)              AS product_id,
    CAST(productovol AS DOUBLE)            AS volume_liters,
    date(from_unixtime(try_cast(fechaultimalect AS bigint))) AS lectura_date,
    from_unixtime(try_cast(fechaultimalect AS bigint))       AS lectura_ts
  FROM copecfuel_staging.telemedicion_detalle
  WHERE CAST(ubicacioncodigo AS INTEGER) = %(client_id)s
    AND protucto IN (1,4,5,6,7)
    AND date(from_unixtime(try_cast(fechaultimalect AS bigint))) BETWEEN date_add('day', -35, current_date) AND current_date
),
-- última lectura de cada domingo por tanque
sunday_last AS (
  SELECT *
  FROM (
    SELECT
      client_id, tank_id, product_id, volume_liters, lectura_date, lectura_ts,
      row_number() OVER (
        PARTITION BY client_id, tank_id, lectura_date
        ORDER BY lectura_ts DESC
      ) AS rn_day
    FROM base
    WHERE day_of_week(lectura_date) = 7   -- 1=Lun … 7=Dom
  ) t
  WHERE rn_day = 1
),
-- 3 domingos más recientes por tanque
last3 AS (
  SELECT *
  FROM (
    SELECT
      client_id, tank_id, product_id, volume_liters, lectura_date,
      row_number() OVER (
        PARTITION BY client_id, tank_id
        ORDER BY lectura_date DESC
      ) AS rn_sunday
    FROM sunday_last
  ) t
  WHERE rn_sunday <= 3
),
with_alias AS (
  SELECT
    client_id,
    tank_id,
    CASE product_id
      WHEN 7 THEN 'Kerosene'
      WHEN 6 THEN 'Gasolina 97'
      WHEN 4 THEN 'Gasolina 93'
      WHEN 5 THEN 'Gasolina 95'
      WHEN 1 THEN 'Petróleo Diésel'
      ELSE CAST(product_id AS VARCHAR)
    END AS product_name,
    product_id,
    volume_liters
  FROM last3
)
SELECT
  client_id,
  tank_id,
  product_name,
  AVG(volume_liters) AS initial_volume_liters
FROM with_alias
GROUP BY client_id, tank_id, product_name
"""

@router.get("/summary", response_model=TelemetrySummary)
def telemetry_summary(client_id: int = Query(..., description="Código EDS")):
    try:
        with get_athena_connection() as conn:
            df_tanks = pd.read_sql(Q1_TANKS, conn, params={"client_id": client_id})
            df_init  = pd.read_sql(Q2_INIT,  conn, params={"client_id": client_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Athena query failed: {e}")

    if df_tanks is None or df_tanks.empty:
        return TelemetrySummary(client_id=client_id, products=[])

    df = pd.merge(
        df_tanks, df_init,
        on=["client_id", "tank_id", "product_name"],
        how="left"
    )
    df["capacity_m3"] = df["capacity_liters"] / 1000.0
    if "initial_volume_liters" not in df.columns:
        df["initial_volume_liters"] = pd.NA
    df["initial_volume_m3"] = df["initial_volume_liters"] / 1000.0

    products: list[ProductSummary] = []
    for pname, g in df.groupby("product_name", dropna=False):
        tanks = [
            TankSummary(
                tank_id=int(row["tank_id"]),
                capacity_liters=float(row["capacity_liters"]),
                capacity_m3=float(row["capacity_m3"]),
                initial_volume_liters=(None if pd.isna(row["initial_volume_liters"]) else float(row["initial_volume_liters"])),
                initial_volume_m3=(None if pd.isna(row["initial_volume_m3"]) else float(row["initial_volume_m3"])),
            )
            for _, row in g.sort_values("tank_id").iterrows()
        ]
        products.append(
            ProductSummary(
                product_name=(None if pd.isna(pname) else str(pname)),
                tanks_count=int(g["tank_id"].nunique()),
                capacity_liters=float(g["capacity_liters"].sum()),
                capacity_m3=float(g["capacity_liters"].sum() / 1000.0),
                initial_product_liters=(None if not g["initial_volume_liters"].notna().any() else float(g["initial_volume_liters"].sum(skipna=True))),
                initial_product_m3=(None if not g["initial_volume_liters"].notna().any() else float(g["initial_volume_liters"].sum(skipna=True) / 1000.0)),
                tanks=tanks
            )
        )

    return TelemetrySummary(client_id=client_id, products=products)
