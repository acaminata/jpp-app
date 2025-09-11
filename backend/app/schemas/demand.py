from pydantic import BaseModel
from typing import List
from datetime import date

class HourlyCurve(BaseModel):
    product_name: str
    hourly_m3: List[float]

class DemandCurveResponse(BaseModel):
    client_id: int
    start_date: date
    end_date: date
    weeks: int
    data_max_date: date
    curves: List[HourlyCurve]
    total_hourly_m3: List[float]
