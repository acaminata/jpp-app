from pydantic import BaseModel
from typing import List, Optional

class TankSummary(BaseModel):
    tank_id: int
    capacity_liters: float
    capacity_m3: float
    initial_volume_liters: Optional[float] = None
    initial_volume_m3: Optional[float] = None

class ProductSummary(BaseModel):
    product_name: Optional[str] = None
    tanks_count: int
    capacity_liters: float
    capacity_m3: float
    initial_product_liters: Optional[float] = None
    initial_product_m3: Optional[float] = None
    tanks: List[TankSummary]

class TelemetrySummary(BaseModel):
    client_id: int
    products: List[ProductSummary]
