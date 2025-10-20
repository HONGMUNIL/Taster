
# 요청마다 고유한 trace_id를 만들어서 에러 응답에 같이 넣는다 좀 더 학습필요;;
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid

class TraceIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.trace_id = uuid.uuid4().hex  # 예: "e3b0c44298fc1c..."
        response = await call_next(request)
        # 응답 헤더에도 넣어두면 클라이언트가 확인하기 편함
        response.headers["X-Trace-Id"] = request.state.trace_id
        return response
