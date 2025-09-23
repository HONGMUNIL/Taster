from typing import Optional

from pydantic import BaseModel, Field


class PlaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=70)
    area_id: int
    category_id: Optional[int] = None

class PlaceRead(BaseModel):
    id: int
    name: str
    area_id: int
    category_id: Optional[int] = None
    area_name: str
    category_name: Optional[str] = None


