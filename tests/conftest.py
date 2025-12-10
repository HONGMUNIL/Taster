

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session

from app.main import create_app
from app.db.session import get_db
from app.models import area, category, place, review, user  # 모델들을 import 해서 메타데이터 등록


#  테스트용 DB 엔진 만들기
#    여기서는 메모리 안에만 존재하는 sqlite 사용
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


#  이 엔진으로 세션 만드는 함수
def get_test_session() -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


# pytest용 fixture  테스트마다 DB 새로 만들고 지우기
@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    #  테이블 생성
    SQLModel.metadata.create_all(test_engine)

    #  앱 생성
    app = create_app()

    #  실제 get_db 대신 테스트용 get_test_session을 쓰도록 덮어쓰기
    app.dependency_overrides[get_db] = get_test_session

    #  TestClient로 감싸서 반환
    with TestClient(app) as c:
        yield c

    #  테스트 끝난 뒤 테이블 전부 삭제
    SQLModel.metadata.drop_all(test_engine)
