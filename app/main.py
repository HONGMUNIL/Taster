
# 서버의 "문" 역할. 여기서 앱을 만들고, 시작할 때 DB 테이블을 준비

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.session import init_db
from app.routers import auth, category


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 켜질 때 딱 한 번 실행: 테이블 만들기
    init_db()
    yield
    #  서버 종료 시 처리할 게 있으면 여기서 하면 돼요 (지금은 없음)


app = FastAPI(
    title="Taster API",
    version="0.1.0",
    lifespan=lifespan,  # on_event 대신 lifespan 사용
)


@app.get("/health")
def health():
    return {"ok": True}

# 기능(라우터) 연결
app.include_router(auth.router)
app.include_router(category.router)

# 로컬 실행용 (선택)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
