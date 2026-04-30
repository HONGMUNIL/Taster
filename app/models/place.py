from typing import Optional

from sqlmodel import SQLModel, Field


class Place(SQLModel, table=True):
    __tablename__ = "places"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    area_id: int = Field(foreign_key="areas.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    status: str = Field(default="pending", max_length=20)