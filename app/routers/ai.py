from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_db
from app.models import Place, Review
from app.schemas.ai import PlaceReviewSummaryResponse
from app.services.ai_service import summarize_reviews_with_ai

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post(
    "/places/{place_id}/summary",
    response_model=PlaceReviewSummaryResponse,
    summary="AI 리뷰 요약",
)
def summarize_place_reviews(
    place_id: int,
    db: Session = Depends(get_db),
):
    place = db.get(Place, place_id)

    if not place:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")

    statement = select(Review).where(Review.place_id == place_id)
    reviews = db.exec(statement).all()

    review_bodies = [review.body for review in reviews]

    ai_result = summarize_reviews_with_ai(review_bodies)

    return PlaceReviewSummaryResponse(
        place_id=place_id,
        review_count=len(review_bodies),
        summary=ai_result.summary,
        positive_keywords=ai_result.positive_keywords,
        negative_keywords=ai_result.negative_keywords,
    )