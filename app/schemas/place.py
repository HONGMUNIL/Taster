from typing import Optional
from sqlmodel import SQLModel


class PlaceCreate(SQLModel):
    name: str
    area_id: int
    category_id: Optional[int] = None


class PlaceRead(SQLModel):
    id: int
    name: str
    area_id: int
    category_id: Optional[int] = None
    area_name: str
    category_name: Optional[str] = None
    avg_rating: Optional[float] = None
    review_count: int = 0
    status: str