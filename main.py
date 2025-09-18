from typing import Optional, List

import app
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import HTTPException

# DB 연결 (SQLite 파일로 저장)
engine = create_engine("sqlite:///taster.db", echo=True)

# Category 테이블 정의
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    slug: str = Field(index=True, unique=True)  # URL-friendly 이름

# 앱 시작할 때 테이블 생성
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# 카테고리 추가 API
@app.post("/categories")
def create_category(name: str, slug: str):
    with Session(engine) as session:
        # slug 중복 체크
        exists = session.exec(select(Category).where(Category.slug == slug)).first()
        if exists:
            raise HTTPException(status_code=400, detail="중복 slug")
        c = Category(name=name, slug=slug)
        session.add(c)
        session.commit()
        session.refresh(c)
        return c

# 카테고리 목록 조회 API
@app.get("/categories", response_model=List[Category])
def list_categories():
    with Session(engine) as session:
        categories = session.exec(select(Category)).all()
        return categories
