from pathlib import Path

# Base project directory (two levels up from this file)
ROOT_DIR = Path(__file__).resolve().parents[2]

# Data directories
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Models directory
MODELS_DIR = ROOT_DIR / "src" / "ML" / "models"

# Default log file
LOG_FILE = ROOT_DIR / "app.log"

# Default scanning settings
DEFAULT_PORT_RANGE = "1-1000"
DEFAULT_WORKERS = 50