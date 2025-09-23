from pydantic import BaseModel, Field, ConfigDict


class AreaCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class AreaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


