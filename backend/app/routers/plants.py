from fastapi import APIRouter, HTTPException
from typing import List
import pandas as pd

from ..deps.athena import get_athena_connection
from ..schemas.plant import Plant

router = APIRouter(prefix="/plants", tags=["plants"])

QUERY = """
SELECT DISTINCT
    werksreal, 
    name1werksreal
FROM logistica_scr_staging.etlist
WHERE
    (auart = 'ZC01' OR auart = 'ZCES')
    AND regexp_like(werksreal, '^[0-9]+$')
    AND CAST(werksreal AS INT) <= 1254
ORDER BY werksreal
"""

@router.get("", response_model=List[Plant])
def list_plants():
    try:
        with get_athena_connection() as conn:
            df = pd.read_sql(QUERY, conn)
        if "werksreal" in df.columns:
            try:
                df["werksreal"] = df["werksreal"].astype(int)
            except Exception:
                pass
        return [Plant(**row.to_dict()) for _, row in df.iterrows()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying Athena: {e}")
