# 패키지를 import하면(예: import app.models) 아래 코드들이 실행됩니다.
from .user import User

# Category가 이미 있다면 함께 등록
# 없다면 try/except로 넘어가면 됩니다.
try:
    from .category import Category
except Exception:
    pass

__all__ = ["User", "Category"]
