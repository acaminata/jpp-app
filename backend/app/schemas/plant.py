from pydantic import BaseModel

class Plant(BaseModel):
    werksreal: int
    name1werksreal: str | None = None
