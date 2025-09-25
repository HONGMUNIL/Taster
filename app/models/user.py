from datetime import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__= "users"
    __table_args__=(UniqueConstraint("email", name="uq_user_email"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)




