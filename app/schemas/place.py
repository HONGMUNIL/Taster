
from typing import Optional
from pydantic import BaseModel, ConfigDict


class PlaceCreate(BaseModel):
    name: str
    area_id: int
    category_id: Optional[int] = None


class PlaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str

    area_id: int
    category_id: Optional[int] = None

    area_name: str
    category_name: Optional[str] = None


    avg_rating: Optional[float] = None
    review_count: int = 0
