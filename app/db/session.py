from sqlmodel import create_engine, Session, SQLModel
from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)

def get_db():
    with Session(engine) as session:
        yield session
