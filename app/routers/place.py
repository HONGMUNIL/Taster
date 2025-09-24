from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.db.session import get_db
from app.models.place import Place
from app.models.area import Area
from app.models.category import Category  # Day 2에서 만든 Category 모델
from app.schemas.place import PlaceCreate, PlaceRead

router = APIRouter(prefix="/places", tags=["places"])


@router.post("", response_model=PlaceRead, status_code=status.HTTP_201_CREATED, summary="Create Place")
def create_place(body: PlaceCreate, db: Session = Depends(get_db)):
    # 1) 지역 확인
    area = db.get(Area, body.area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")

    # 2) 카테고리 확인(선택)
    cat = None
    if body.category_id is not None:
        cat = db.get(Category, body.category_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found")

    # 3) 저장
    place = Place(name=body.name, area_id=body.area_id, category_id=body.category_id)
    db.add(place)
    db.commit()
    db.refresh(place)

    # 4) 읽기 편하게
    return PlaceRead(
        id=place.id,
        name=place.name,
        area_id=place.area_id,
        category_id=place.category_id,
        area_name=area.name,
        category_name=(cat.name if cat else None),
    )


@router.get("", response_model=List[PlaceRead], summary="검색/필터/페이지")
def list_places(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="가게 이름에 이 글자가 들어간 것만"),
    area_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    # 1) 필터 적용
    stmt = select(Place)
    if q:
        stmt = stmt.where(Place.name.contains(q))
    if area_id is not None:
        stmt = stmt.where(Place.area_id == area_id)
    if category_id is not None:
        stmt = stmt.where(Place.category_id == category_id)

    stmt = stmt.order_by(Place.name).offset(skip).limit(limit)
    rows = db.exec(stmt).all()

    # 2) 이름 채우기 위한 간단 캐시
    areas_cache: dict[int, Area] = {}
    cats_cache: dict[int, Category] = {}

    results: List[PlaceRead] = []
    for p in rows:
        area = areas_cache.get(p.area_id)
        if area is None:
            area = db.get(Area, p.area_id)
            if area:
                areas_cache[p.area_id] = area

        cat_name = None
        if p.category_id is not None:
            cat = cats_cache.get(p.category_id)
            if cat is None:
                cat = db.get(Category, p.category_id)
                if cat:
                    cats_cache[p.category_id] = cat
            cat_name = cat.name if cat else None

        results.append(
            PlaceRead(
                id=p.id,
                name=p.name,
                area_id=p.area_id,
                category_id=p.category_id,
                area_name=area.name if area else "unknown",
                category_name=cat_name,
            )
        )

    return results
