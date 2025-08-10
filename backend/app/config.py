from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Directories
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
DATA_DIR = BACKEND_DIR / "data"

# SQLite database file path
DB_PATH = APP_DIR / "app.db"

# External configuration
HOSTAWAY_ACCOUNT_ID = os.getenv("HOSTAWAY_ACCOUNT_ID", "61148")
HOSTAWAY_API_KEY = os.getenv("HOSTAWAY_API_KEY", "")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
HOSTAWAY_LIVE_MODE = os.getenv("HOSTAWAY_LIVE_MODE", "false").lower() in {
    "1",
    "true",
    "yes",
}
HOSTAWAY_API_BASE = os.getenv("HOSTAWAY_API_BASE", "https://api.hostaway.com/v1")

# Frontend may consume the API at this base URL; Streamlit can override via env
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
