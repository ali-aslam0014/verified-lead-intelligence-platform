import logging
import sys
from app.core.config import settings


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("lead_intel")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

    # Remove default handlers if present
    for handler in logger.handlers:
        logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    
    if settings.ENVIRONMENT.lower() == "production":
        try:
            from pythonjsonlogger import jsonlogger
            formatter = jsonlogger.JsonFormatter(
                "%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s"
            )
        except ImportError:
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] [%(name)s] [%(request_id)s] %(message)s"
            )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | req_id=%(request_id)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = setup_logging()
