from dbm import error

from starlette.testclient import TestClient


def test_create_category_duplicate_name(client: TestClient):
    # 카테고리 생성
    resp1 = client.post(
        "/category",
        json={"name": "라멘", "description": "라멘 가게"},

    )
    assert resp1.status_code ==201
    data1 = resp1.json()
    assert  data1["name"] == "라멘"

    # 같은 이름으로 다시 생성 + 409에러 나와야함
    resp2 = client.post(
        "/category",
        json={"name": "라멘", "description": "이상한 다른 설명"},
    )
    assert resp2.status_code == 409

    # 에러 응답 포멧
    body = resp2.json()
    assert "error" in body

    error = body["error"]

    assert error["code"] == "HTTP_409"

    assert error["message"] == "Category already exists"

    assert "trace_id" in error
    assert isinstance(error["trace_id"], str)
    assert error["trace_id"] != ""

# tests/conftest.py

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session

from app.main import create_app
from app.db.session import get_db
from app.models import area, category, place, review, user  # 모델들을 import 해서 메타데이터 등록


# 1) 테스트용 DB 엔진 만들기
#    메모리(:memory:) 대신, 파일로 된 sqlite를 사용
TEST_DATABASE_URL = "sqlite:///./test_taster.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# 2) 이 엔진으로 세션 만드는 함수
def get_test_session() -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


# 3) pytest용 fixture  테스트마다 DB 새로 만들고 지우기
@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    # 테이블 생성
    SQLModel.metadata.create_all(test_engine)

    # 앱 생성
    app = create_app()

    # 실제 get_db 대신 테스트용 get_test_session을 쓰도록 덮어쓰기
    app.dependency_overrides[get_db] = get_test_session

    # TestClient로 감싸서 반환
    with TestClient(app) as c:
        yield c

    # 테스트 끝난 뒤 테이블 전부 삭제
    SQLModel.metadata.drop_all(test_engine)
