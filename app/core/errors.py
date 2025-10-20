from typing import Any, List, Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

def _make_error(message: str, code: str, trace_id: str,
                details: Any = None, field_errors: List[Dict] | None = None) -> dict:
    body = {
        "error": {
            "code": code,
            "message": message,
            "trace_id": trace_id,
        }
    }
    if details is not None:
        body["error"]["details"] = details
    if field_errors:
        body["error"]["field_errors"] = field_errors
    return body

# 1) HTTPException (FastAPI가 자주 쓰는 에러)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    trace_id = getattr(request.state, "trace_id", "n/a")
    # detail이 문자열일 수도, dict일 수도 있음 둘 다 처리
    if isinstance(exc.detail, dict):
        message = exc.detail.get("message") or exc.detail.get("detail") or "Error"
        code = exc.detail.get("code") or f"HTTP_{exc.status_code}"
        details = exc.detail.get("details")
    else:
        message = str(exc.detail) if exc.detail else "Error"
        code = f"HTTP_{exc.status_code}"
        details = None

    body = _make_error(message=message, code=code, trace_id=trace_id, details=details)
    headers = getattr(exc, "headers", None)  # (예: 401 응답의 WWW-Authenticate)
    return JSONResponse(status_code=exc.status_code, content=body, headers=headers)

# 2) 요청 검증 실패
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    trace_id = getattr(request.state, "trace_id", "n/a")
    field_errors = []

    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", []))
        field_errors.append({"loc": loc, "msg": err.get("msg"), "type": err.get("type")})
    body = _make_error(
        message="Invalid request",
        code="VALIDATION_ERROR",
        trace_id=trace_id,
        field_errors=field_errors,
    )
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body)

# 3)따 로 처리하지 않은 모든 예외
async def unhandled_exception_handler(request: Request, exc: Exception):
    trace_id = getattr(request.state, "trace_id", "n/a")
    body = _make_error(
        message="Internal server error",
        code="INTERNAL_SERVER_ERROR",
        trace_id=trace_id,
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body)
