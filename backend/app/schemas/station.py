from pydantic import BaseModel
from typing import Optional

class Station(BaseModel):
    plant_id: int
    plant_name: Optional[str] = None
    client_id: int
    client_description: Optional[str] = None
    zone_id: Optional[str] = None
    zone_name: Optional[str] = None
    zone_manager_name: Optional[str] = None
    truck_type: Optional[str] = None
