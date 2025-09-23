from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


class Area(SQLModel, table=True):
    __tablename__ = "areas"
    __table_args__ = (UniqueConstraint("name", name="uq_areas_name"))

    id: Optional[int] = Field(defalut=None, primary_key=True)
    name: str = Field(index=True)

    


