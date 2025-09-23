from datetime import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint, ForeignKey
from sqlmodel import SQLModel, Field


class Place(SQLModel, table=True):
    __tablename__ = "places"
    __table_args__ = (UniqueConstraint("name", name="uq_place_name"))

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    #외래키: areas.id 로 연결!!
    area_id: int = Field(foreign_key="areas.id", index=True)
    #외래키: category.id로 연결!!
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", index=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
