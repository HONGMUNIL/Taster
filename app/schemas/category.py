from typing import Optional
from sqlmodel import SQLModel


class CategoryBase(SQLModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
