import logging
from pathlib import Path

from .config import LOG_FILE

# Ensure log directory exists
log_path = Path(LOG_FILE)
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the configured settings."""
    return logging.getLogger(name)