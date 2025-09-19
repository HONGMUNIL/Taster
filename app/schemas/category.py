from typing import Optional
from datetime import datetime
from pydantic import ConfigDict
from sqlmodel import SQLModel

class CategoryCreate(SQLModel):
    name: str
    description: Optional[str] = None

class CategoryRead(SQLModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # ORM 객체 -> 응답 변환 허용
    model_config = ConfigDict(from_attributes=True)
