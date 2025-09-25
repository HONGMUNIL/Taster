from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    place_id: int = Field(foreign_key="places.id", index=True)
    rating: int
    body: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)



