# app/routers/ranking.py
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlmodel import Session, select

from app.db.session import get_db
from app.models.place import Place
from app.models.review import Review
from app.schemas.ranking import PlaceRankRead

router = APIRouter(prefix="/rankings", tags=["rankings"])


def _compute_bayes_score(R: Optional[float], v: int, C: float, m: int) -> float:
    """
    R: 해당 가게 평균 별점
    v: 해당 가게 리뷰 수
    C: 전체 평균 별점
    m: 최소 리뷰 수(가중치)
    """
    if v <= 0 or R is None:
        return float(C)
    return float((v / (v + m)) * R + (m / (v + m)) * C)


@router.get("", response_model=List[PlaceRankRead], summary="베이지안 평균 랭킹")
def list_rankings(
    db: Session = Depends(get_db),
    area_id: Optional[int] = Query(None, description="특정 지역만"),
    category_id: Optional[int] = Query(None, description="특정 카테고리만"),
    m: int = Query(10, ge=1, le=1000, description="최소 리뷰 수 가중치"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    # 1) 전체 평균 C
    avg_q = select(func.avg(Review.rating)).select_from(Review)
    if area_id is not None or category_id is not None:
        avg_q = avg_q.join(Place, Review.place_id == Place.id)
        if area_id is not None:
            avg_q = avg_q.where(Place.area_id == area_id)
        if category_id is not None:
            avg_q = avg_q.where(Place.category_id == category_id)

    avg_row = db.exec(avg_q).one_or_none()  # 환경에 따라 float 또는 (float,)가 나올 수 있음
    if isinstance(avg_row, tuple):
        avg_val = avg_row[0]
    else:
        avg_val = avg_row
    C = float(avg_val) if avg_val is not None else 0.0

    # 2) 가게별 v, R 집계
    stmt = (
        select(
            Place.id.label("place_id"),
            Place.name.label("place_name"),
            func.count(Review.id).label("v"),
            func.avg(Review.rating).label("R"),
        )
        .select_from(Place)  # 기준 테이블 명시
        .join(Review, Review.place_id == Place.id, isouter=True)
    )
    if area_id is not None:
        stmt = stmt.where(Place.area_id == area_id)
    if category_id is not None:
        stmt = stmt.where(Place.category_id == category_id)
    stmt = stmt.group_by(Place.id)

    rows = db.exec(stmt).all()

    # 3) 베이지안 점수 계산
    ranked: List[PlaceRankRead] = []
    for place_id, place_name, v, R in rows:
        v = int(v or 0)
        R_val: Optional[float] = float(R) if R is not None else None
        score = _compute_bayes_score(R_val, v, C, m)
        ranked.append(
            PlaceRankRead(
                place_id=place_id,
                place_name=place_name,
                bayes_score=round(score, 6),
                avg_rating=(round(R_val, 6) if R_val is not None else None),
                review_count=v,
            )
        )

    # 4) 정렬 및 페이지
    ranked.sort(key=lambda x: x.bayes_score, reverse=True)
    return ranked[skip : skip + limit]
