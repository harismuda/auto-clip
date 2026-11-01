import os
from pathlib import Path
from dotenv import load_dotenv

# Path Direktori
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent

# Load .env (cek di backend/.env lalu root/.env)
if (BACKEND_DIR / ".env").exists():
    load_dotenv(BACKEND_DIR / ".env")
elif (ROOT_DIR / ".env").exists():
    load_dotenv(ROOT_DIR / ".env")
else:
    load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Folder penyimpanan
TEMP_DIR = BACKEND_DIR / "temp"
OUTPUT_DIR = ROOT_DIR / "output"

TEMP_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Format & Durasi Klip Default
DEFAULT_MIN_CLIP_DURATION = 20  # detik
DEFAULT_MAX_CLIP_DURATION = 65  # detik
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920

