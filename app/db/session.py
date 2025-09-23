from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# SQLite일 때만 필요한 옵션
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

# echo=False(로그 깔끔), pool_pre_ping=True(죽은 커넥션 자동 복구)
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
)

#  모든 모델 로드
import app.models  # noqa: F401


def get_db():
    # 요청마다 세션을 열고 닫는 FastAPI 기본 패턴
    with Session(engine) as session:
        yield session


def init_db():
    # 테이블 생성
    SQLModel.metadata.create_all(engine)
