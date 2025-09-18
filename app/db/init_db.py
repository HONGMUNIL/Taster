from sqlmodel import SQLModel
from app.db.session import engine

def init_db() -> None:
    # models import가 metadata에 등록되게 필요한 모델을 불러와야 함
    from app.models.category import Category  # noqa: F401
    SQLModel.metadata.create_all(engine)
