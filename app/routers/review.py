from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Query
from fastapi.params import Depends
from sqlmodel import Session, select

from app.db.session import get_db
from app.models import User, Place, Review
from app.routers.auth import get_current_user # 로그인 검증
from app.schemas.review import ReviewCreate, ReviewRead

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED, summary="리뷰 작성(로그인한사람만)")
def create_review(
        body: ReviewCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    if len(body.body) < 20:
        raise HTTPException(status_code=400, detail="리뷰 글자수는 최소 20자 입니다.")

    # 1) 가게 존재 확인
    place = db.get(Place, body.place_id)
    if not place:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")

    item = Review(
        user_id=current_user.id,
        place_id=body.place_id,
        rating=body.rating,
        body=body.body,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    # 3) 응답( 보기 좋게)
    return ReviewRead(
        id=item.id,
        place_id=item.place_id,
        rating=item.rating,
        body=item.body,
        created_at=item.created_at.isoformat(),
        author_email=current_user.email,
    )


@router.get("", response_model=List[ReviewRead], summary="리뷰 목록")
def list_reviews(
        db: Session = Depends(get_db),
        place_id: Optional[int] = Query(None, description="특정 가게 리뷰만 추출"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Review)
    if place_id is not None:
        stmt = stmt.where(Review.place_id == place_id)
    stmt = stmt.order_by(Review.created_at.desc()).offset(skip).limit(limit)

    rows = db.exec(stmt).all()

    # 작성자 이메일 넣기
    results: List[ReviewRead] = []
    for r in rows:
        # 작성자 이메일 조회
        author = db.get(User, r.user_id)
        results.append(
            ReviewRead(
                id=r.id,
                place_id=r.place_id,
                rating=r.rating,
                body=r.body,
                created_at=r.created_at.isoformat(),
                author_email=(author.email if author else None),

            )
        )
    return results


