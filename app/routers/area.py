from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select


from app.db.session import get_db
from app.models.area import Area
from app.schemas.area import AreaCreate, AreaRead


router = APIRouter(prefix="/areas", tags=["areas"])


@router.get("", response_model=List[AreaRead])
def list_areas(db: Session = Depends(get_db)):
    items = db.exec(select(Area).order_by(Area.name)).all()
    return items


@router.post("", response_model=AreaRead, status_code=status.HTTP_201_CREATED)
def create_area(body: AreaCreate, db: Session = Depends(get_db)):
    exists = db.exec(select(Area).where(Area.name == body.name)).first()
    if exists:
        raise HTTPException(status_code=409, detail="Area already exists")
    item = Area(name=body.name)
    db.add(item); db.commit(); db.refresh(item)
    return item