from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, select
from app.db.session import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_model=list[CategoryRead], summary="List Categories")
def list_categories(db: Session = Depends(get_db)):
    return db.exec(select(Category)).all()

@router.post("", response_model=CategoryRead, status_code=201, summary="Create Category")
def create_category(body: CategoryCreate, db: Session = Depends(get_db)):
    exists = db.exec(select(Category).where(Category.name == body.name)).first()
    if exists:
        raise HTTPException(409, "Category already exists")
    item = Category(name=body.name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
