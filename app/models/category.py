from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String, Text, DateTime, func

class CategoryBase(SQLModel):
    name: str
    description: Optional[str] = None

class Category(CategoryBase, table=True):
    __tablename__ = "category"

    id: Optional[int] = Field(default=None, primary_key=True)

    # unique, index, not null
    name: str = Field(
        sa_column=Column(String(100), unique=True, index=True, nullable=False)
    )
    description: Optional[str] = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )

    created_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
    )
