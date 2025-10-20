# 서버의 문 느낌. 여기서 앱 만들고 시작할 때 DB 테이블 준비

from contextlib import asynccontextmanager
from fastapi import FastAPI

# 예외 타입
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.middleware import TraceIDMiddleware
from app.core.errors import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)

from app.db.session import init_db
from app.routers import auth, category, area, place, review


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 켜질 때 딱 한 번 실행- 테이블 만들기
    init_db()
    yield
    # 서버 종료 시 처리할 게 있으면 여기서 하면 됌 (지금은 없음)


app = FastAPI(
    title="Taster API",
    version="0.1.0",
    lifespan=lifespan,  # on_event 대신 lifespan 사용
)

#  요청마다 trace_id 달아주는 미들웨어 추가
app.add_middleware(TraceIDMiddleware)

# 예외 핸들러 등록 (HTTPException / 422검증오류 / 나머지모든에러)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/health")
def health():
    return {"ok": True}

# 기능(라우터) 연결
app.include_router(auth.router)
app.include_router(category.router)
app.include_router(area.router)
app.include_router(place.router)
app.include_router(review.router)

# 로컬 실행용
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
