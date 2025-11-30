from typing import Optional
from pydantic import BaseModel, ConfigDict

class PlaceRankRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    place_id: int
    place_name: str
    bayes_score: float          # 베이지안 점수
    avg_rating: Optional[float] = None  # 평균
    review_count: int
