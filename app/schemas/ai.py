from pydantic import BaseModel, Field


class AIReviewSummary(BaseModel):
    summary: str = Field(description="리뷰 전체 요약")
    positive_keywords: list[str] = Field(description="긍정 키워드 목록")
    negative_keywords: list[str] = Field(description="부정 키워드 목록")


class PlaceReviewSummaryResponse(BaseModel):
    place_id: int
    review_count: int
    summary: str
    positive_keywords: list[str]
    negative_keywords: list[str]