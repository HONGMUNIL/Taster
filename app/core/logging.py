import logging
import sys
from app.core.config import settings

def setup_logging():
    root = logging.getLogger()
    if root.handlers:
        return

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    fmt = "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
    handler.setFormatter(logging.Formatter(fmt))

    root.setLevel(level)
    root.addHandler(handler)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).setLevel(level)
