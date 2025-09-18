from sqlmodel import Session, create_engine
from app.core.config import settings

# SQLite일 때만 필요한 옵션
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, echo=True, connect_args=connect_args,)


#yield는 함수 잠깐 멈추고 요청끝나면 자동으로 나머지 finally까지 실행( DB연결 관리때문에 편함)
def get_db():
    with Session(engine) as session:
        yield session






