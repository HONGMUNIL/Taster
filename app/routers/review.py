from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Query, Response
from fastapi.params import Depends
from sqlmodel import Session, select

from app.db.session import get_db
from app.models import User, Place, Review
from app.routers.auth import get_current_user
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED, summary="리뷰 작성(로그인한사람만)")
def create_review(
        body: ReviewCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    # 본문 길이 체크
    if len(body.body) < 10:
        raise HTTPException(status_code=400, detail="리뷰 글자수는 최소 10자 입니다.")

    #  가게 존재 확인
    place = db.get(Place, body.place_id)
    if not place:
        raise HTTPException(status_code=404, detail="가게를 찾을 수 없습니다.")

    #  같은 유저가 같은 가게에 이미 리뷰를 썼는지 확인
    exists_stmt = select(Review).where(
        Review.user_id == current_user.id,
        Review.place_id == body.place_id,
    )
    exists = db.exec(exists_stmt).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 이 가게에 작성한 리뷰가 있습니다.",
        )

    #  새 리뷰 저장
    item = Review(
        user_id=current_user.id,
        place_id=body.place_id,
        rating=body.rating,
        body=body.body,
    )
    db.add(item)
    db.commit()
    db.refresh(item)

    #  응답
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
        user_id: Optional[int] = Query(None, description="특정 사용자가 쓴 리뷰만 추출"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Review)

    if place_id is not None:
        stmt = stmt.where(Review.place_id == place_id)

    if user_id is not None:
        stmt = stmt.where(Review.user_id == user_id)

    stmt = stmt.order_by(Review.created_at.desc()).offset(skip).limit(limit)

    rows = db.exec(stmt).all()

    results: List[ReviewRead] = []
    for r in rows:
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


@router.put(
    "/{review_id}",
    response_model=ReviewRead,
    summary="리뷰 수정(작성자만!!)",
)
def update_review(
        review_id: int,
        body: ReviewUpdate,
        current_user: User = Depends(get_current_user),
        db:Session = Depends(get_db),
):
    # 리뷰 찾기
    item = db.get(Review, review_id)
    if not item:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")

    # 작성쟈인지 확인
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인이 작성한 리뷰만 수정할 수 있습니다.")

    # 글자 수 체크
    if len(body.body) < 10:
        raise HTTPException(status_code=400, detail="리뷰 글자수는 최소 10자 입니다")

    # 값 수정
    item.rating = body.rating
    item.body = body.body
    db.add(item)
    db.commit()
    db.refresh(item)

    #  응답
    return ReviewRead(
        id=item.id,
        place_id=item.place_id,
        rating=item.rating,
        body=item.body,
        created_at=item.created_at.isoformat(),
        author_email=current_user.email,
    )


@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="리뷰 삭제(작성자만)",
)
def delete_review(
        review_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    #  리뷰 찾기
    item = db.get(Review, review_id)
    if not item:
        raise HTTPException(status_code=404, detail="리뷰를 찾을 수 없습니다.")

    #  작성자인지 확인
    if item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인이 작성한 리뷰만 삭제할 수 있습니다.")

    #  삭제
    db.delete(item)
    db.commit()

    #  내용 없는 204 응답
    return Response(status_code=status.HTTP_204_NO_CONTENT)





