import os
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = APP_ROOT.parent
UPLOAD_DIR = PROJECT_ROOT / "uploads"
DB_PATH = PROJECT_ROOT / "grade9_planner.db"
MATPLOTLIB_CONFIG_DIR = PROJECT_ROOT / ".cache" / "matplotlib"


UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MATPLOTLIB_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MATPLOTLIB_CONFIG_DIR))
