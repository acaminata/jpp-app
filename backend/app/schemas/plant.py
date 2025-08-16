from pydantic import BaseModel

class Plant(BaseModel):
    plant_id: int
    plant_name: str | None = None
