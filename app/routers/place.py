from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlmodel import Session, select

from app.db.session import get_db
from app.models.place import Place
from app.models.area import Area
from app.models.category import Category
from app.models.review import Review
from app.models.user import User
from app.schemas.place import PlaceCreate, PlaceRead
from app.routers.auth import get_current_user

router = APIRouter(prefix="/places", tags=["places"])


@router.post("", response_model=PlaceRead, status_code=status.HTTP_201_CREATED, summary="Create Place")
def create_place(
    body: PlaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    normalized_name = body.name.strip()

    if not normalized_name:
        raise HTTPException(status_code=400, detail="가게 이름은 비워둘 수 없습니다.")

    area = db.get(Area, body.area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")

    cat = None
    if body.category_id is not None:
        cat = db.get(Category, body.category_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

    exists_stmt = select(Place).where(
        func.lower(Place.name) == normalized_name.lower(),
        Place.area_id == body.area_id,
    )
    exists = db.exec(exists_stmt).first()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="같은 지역에 같은 이름의 가게가 이미 등록되어 있습니다.",
        )

    place = Place(
        name=normalized_name,
        area_id=body.area_id,
        category_id=body.category_id,
        status="pending",
    )
    db.add(place)
    db.commit()
    db.refresh(place)

    return PlaceRead(
        id=place.id,
        name=place.name,
        area_id=place.area_id,
        category_id=place.category_id,
        area_name=area.name,
        category_name=(cat.name if cat else None),
        avg_rating=None,
        review_count=0,
        status=place.status,
    )


@router.get("", response_model=List[PlaceRead], summary="검색/필터/정렬/페이지")
def list_places(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="가게 이름에 이 글자가 들어간 것만"),
    area_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="이 별점 이상인 가게만 필터"),
    sort_by: str = Query("avg_rating", description="정렬 기준: name, avg_rating, review_count"),
    sort_order: str = Query("desc", description="정렬 방향: asc 또는 desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
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

    stmt = (
        select(
            Place.id,
            Place.name,
            Place.area_id,
            Place.category_id,
            Place.status,
            Area.name.label("area_name"),
            Category.name.label("category_name"),
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        )
        .select_from(Place)
        .join(Area, Area.id == Place.area_id)
        .join(Category, Category.id == Place.category_id, isouter=True)
        .join(Review, Review.place_id == Place.id, isouter=True)
        .where(Place.status == "approved")
    )

    if q:
        stmt = stmt.where(Place.name.contains(q))
    if area_id is not None:
        stmt = stmt.where(Place.area_id == area_id)
    if category_id is not None:
        stmt = stmt.where(Place.category_id == category_id)

    stmt = stmt.group_by(
        Place.id,
        Place.name,
        Place.area_id,
        Place.category_id,
        Place.status,
        Area.name,
        Category.name,
    )

    rows = db.exec(stmt).all()

    places: List[PlaceRead] = []
    for row in rows:
        (
            place_id,
            name,
            area_id_val,
            category_id_val,
            status_val,
            area_name,
            category_name,
            avg_rating,
            review_count,
        ) = row

        avg_val = float(avg_rating) if avg_rating is not None else None
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
                status=status_val,
            )
        )

    if min_rating is not None:
        places = [
            p for p in places
            if p.avg_rating is not None and p.avg_rating >= min_rating
        ]

    reverse = sort_order == "desc"

    if sort_by == "name":
        places.sort(key=lambda p: p.name.lower(), reverse=reverse)
    elif sort_by == "review_count":
        places.sort(key=lambda p: p.review_count, reverse=reverse)
    else:
        places.sort(key=lambda p: (p.avg_rating or 0.0), reverse=reverse)

    return places[skip: skip + limit]


@router.get("/{place_id}", response_model=PlaceRead, summary="가게 상세 조회")
def get_place(place_id: int, db: Session = Depends(get_db)):
    place = db.get(Place, place_id)
    if not place or place.status != "approved":
        raise HTTPException(status_code=404, detail="Place not found")

    area = db.get(Area, place.area_id)
    category = db.get(Category, place.category_id) if place.category_id is not None else None

    review_stmt = select(
        func.avg(Review.rating),
        func.count(Review.id),
    ).where(Review.place_id == place_id)

    avg_rating, review_count = db.exec(review_stmt).one()

    avg_val = float(avg_rating) if avg_rating is not None else None
    review_count_int = int(review_count or 0)

    return PlaceRead(
        id=place.id,
        name=place.name,
        area_id=place.area_id,
        category_id=place.category_id,
        area_name=(area.name if area else "알 수 없음"),
        category_name=(category.name if category else None),
        avg_rating=avg_val,
        review_count=review_count_int,
        status=place.status,
    )


@router.patch("/{place_id}/approve", response_model=PlaceRead, summary="가게 승인(개발용 임시)")
def approve_place(
    place_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    place = db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    place.status = "approved"
    db.add(place)
    db.commit()
    db.refresh(place)

    area = db.get(Area, place.area_id)
    category = db.get(Category, place.category_id) if place.category_id is not None else None

    review_stmt = select(
        func.avg(Review.rating),
        func.count(Review.id),
    ).where(Review.place_id == place_id)

    avg_rating, review_count = db.exec(review_stmt).one()

    avg_val = float(avg_rating) if avg_rating is not None else None
    review_count_int = int(review_count or 0)

    return PlaceRead(
        id=place.id,
        name=place.name,
        area_id=place.area_id,
        category_id=place.category_id,
        area_name=(area.name if area else "알 수 없음"),
        category_name=(category.name if category else None),
        avg_rating=avg_val,
        review_count=review_count_int,
        status=place.status,
    )