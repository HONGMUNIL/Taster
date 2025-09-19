from fastapi import FastAPI
from sqlmodel import SQLModel
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine
from app.routers.category import router as category_router

def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(category_router)

    if settings.AUTO_CREATE_TABLES:
        SQLModel.metadata.create_all(engine)

    return app

app = create_app()
