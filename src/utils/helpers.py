import json
from pathlib import Path
from typing import Any

from .logger import get_logger

logger = get_logger(__name__)


def load_json(path: str | Path, default: Any = None) -> Any:
    """Load JSON data from a file."""
    p = Path(path)
    if p.exists():
        with p.open('r', encoding='utf-8') as f:
            return json.load(f)
    logger.warning(f"JSON file not found: {p}")
    return default if default is not None else []


def save_json(data: Any, path: str | Path) -> None:
    """Save data as JSON."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved JSON to {p}")