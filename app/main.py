# app/main.py
# 이 파일은 FastAPI 앱의 "문"이라고 생각하면 돼요.
# 서버가 켜질 때 제일 먼저 읽히고, 각 기능(라우터)을 여기에 붙입니다.

from fastapi import FastAPI

# Day 2에서 만든 카테고리 API, Day 3에서 만든 인증 API를 가져와요.
# 아직 없으면 주석 처리해도 됩니다.
from app.routers import auth, category


def create_app() -> FastAPI:
    """
    앱을 만들어서 돌려주는 함수예요.
    - 제목, 버전 같은 기본 정보를 넣고
    - 주소(엔드포인트)들을 연결해요.
    """
    app = FastAPI(
        title="Taster API",
        version="0.1.0",
        description="맛집 리뷰/랭킹 + 챗봇을 위한 FastAPI 백엔드"
    )

    # 헬스체크: 서버가 살아있는지 확인하는 아주 간단한 엔드포인트
    @app.get("/health")
    def health():
        return {"ok": True}

    # 여기서 기능(라우터)들을 앱에 붙힌다
    # auth: 회원가입/로그인/JWT
    app.include_router(auth.router)

    # categories: 카테고리 목록/생성 (Day 2)
    app.include_router(category.router)

    return app


# uvicorn이 찾을 실제 앱 객체
app = create_app()

# 로컬에서 바로 실행하고 싶다면:
#   python -m app.main
# 또는
#   uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
