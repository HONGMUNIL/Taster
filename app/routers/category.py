from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.db.session import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=List[CategoryRead], summary="List Categories")
def list_categories(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    items = db.exec(select(Category).offset(skip).limit(limit)).all()
    return items

@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, summary="Create Category")
def create_category(body: CategoryCreate, db: Session = Depends(get_db)):
    exists = db.exec(select(Category).where(Category.name == body.name)).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category already exists")

    item = Category(name=body.name, description=body.description)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.get("/{category_id}", response_model=CategoryRead, summary="Get Category")
def get_category(category_id: int, db: Session = Depends(get_db)):
    item = db.get(Category, category_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return item
