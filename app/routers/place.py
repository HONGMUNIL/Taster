
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.db.session import get_db
from app.models.place import Place
from app.models.area import Area
from app.models.category import Category
from app.models.review import Review
from app.schemas.place import PlaceCreate, PlaceRead

router = APIRouter(prefix="/places", tags=["places"])


@router.post("", response_model=PlaceRead, status_code=status.HTTP_201_CREATED, summary="Create Place")
def create_place(body: PlaceCreate, db: Session = Depends(get_db)):
    #  지역 확인
    area = db.get(Area, body.area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")

    # 카테고리 확인
    cat = None
    if body.category_id is not None:
        cat = db.get(Category, body.category_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

    #  저장
    place = Place(name=body.name, area_id=body.area_id, category_id=body.category_id)
    db.add(place)
    db.commit()
    db.refresh(place)

    # 응답
    return PlaceRead(
        id=place.id,
        name=place.name,
        area_id=place.area_id,
        category_id=place.category_id,
        area_name=area.name,
        category_name=(cat.name if cat else None),
        # avg_rating, review_count는 기본값
    )


@router.get("", response_model=List[PlaceRead], summary="검색/필터/정렬/페이지")
def list_places(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="가게 이름에 이 글자가 들어간 것만"),
    area_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(
        None,
        ge=0,
        le=5,
        description="이 별점 이상인 가게만 필터 ",
    ),
    sort_by: str = Query(
        "avg_rating",
        description="정렬 기준: name, avg_rating, review_count",
    ),
    sort_order: str = Query(
        "desc",
        description="정렬 방향: asc 또는 desc",
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    #  sort_by, sort_order 검증
    allowed_sort = {"name", "avg_rating", "review_count"}
    if sort_by not in allowed_sort:
        raise HTTPException(
            status_code=400,
            detail="sort_by는 name, avg_rating, review_count 중 하나여야 합니다.",
        )
    if sort_order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=400,
            detail="sort_order는 asc 또는 desc 여야 합니다.",
        )

    #   Place 기준으로 Area, Category, Review를 조인해서
    #    가게별 평균 별점(avg_rating), 리뷰 수(review_count)를 한 번에 뽑는다.
    stmt = (
        select(
            Place.id,
            Place.name,
            Place.area_id,
            Place.category_id,
            Area.name.label("area_name"),
            Category.name.label("category_name"),
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        )
        .select_from(Place)
        .join(Area, Area.id == Place.area_id)
        .join(Category, Category.id == Place.category_id, isouter=True)
        .join(Review, Review.place_id == Place.id, isouter=True)
    )

    #  필터 적용 (이름, 지역, 카테고리)
    if q:
        stmt = stmt.where(Place.name.contains(q))
    if area_id is not None:
        stmt = stmt.where(Place.area_id == area_id)
    if category_id is not None:
        stmt = stmt.where(Place.category_id == category_id)

    #  그룹화 (가게당 한 줄)
    stmt = stmt.group_by(
        Place.id,
        Place.name,
        Place.area_id,
        Place.category_id,
        Area.name,
        Category.name,
    )

    rows = db.exec(stmt).all()

    #  파이썬 객체로 변환
    places: List[PlaceRead] = []
    for row in rows:
        (
            place_id,
            name,
            area_id_val,
            category_id_val,
            area_name,
            category_name,
            avg_rating,
            review_count,
        ) = row

        avg_val: Optional[float]
        if avg_rating is None:
            avg_val = None
        else:
            avg_val = float(avg_rating)

        review_count_int = int(review_count or 0)

        places.append(
            PlaceRead(
                id=place_id,
                name=name,
                area_id=area_id_val,
                category_id=category_id_val,
                area_name=area_name,
                category_name=category_name,
                avg_rating=avg_val,
                review_count=review_count_int,
            )
        )

    #  최소 별점 필터 (평균 별점 기준)
    if min_rating is not None:
        places = [
            p
            for p in places
            if p.avg_rating is not None and p.avg_rating >= min_rating
        ]

    #  정렬
    reverse = sort_order == "desc"

    if sort_by == "name":
        places.sort(key=lambda p: p.name.lower(), reverse=reverse)
    elif sort_by == "review_count":
        places.sort(key=lambda p: p.review_count, reverse=reverse)
    else:  # avg_rating
        places.sort(key=lambda p: (p.avg_rating or 0.0), reverse=reverse)

    # 페이지 처리
    return places[skip : skip + limit]
