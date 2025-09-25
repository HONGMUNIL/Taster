from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ReviewCreate(BaseModel):
    place_id: int
    rating: int = Field(ge=1, le=5)
    body: str = Field(min_length=5, max_length=1000)

class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True) #ORM 객체에서 읽어오려면 필요함
    id: int
    place_id: int
    rating: int
    body: str
    created_at: str

    author_email: Optional[str] = None


