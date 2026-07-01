from loguru import logger
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

logger.add(
    "logs/application.log",
    rotation="10 MB",
    retention="10 days",
    level="INFO"
)
