from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.routers.categories import router as categories_router
from app.db.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    #  앱이 켜질 때 1번
    setup_logging(settings.DEBUG)
    init_db()
    # (필요하면) DB 초기화, 연결 풀 준비 등

    # 앱이 돌아가는 동안
    yield

    #  앱이 꺼질 때 1번
    # (필요하면) DB 연결 정리 등

def create_app() -> FastAPI:
    api = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

    @api.get("/health", tags=["system"])
    def health():
        return {"status": "ok"}

    #  라우터 연결 (동작)
    api.include_router(categories_router, prefix="/api")

    return api
