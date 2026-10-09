from dotenv import load_dotenv
import os

from config.runtime import APP_DIR

load_dotenv(APP_DIR / ".env")

DEFAULT_SETTINGS = {
    "movies_path": os.getenv("MOVIES_PATH", ""),
    "series_path": os.getenv("SERIES_PATH", ""),
    "tmdb_api_key": os.getenv("TMDB_API_KEY", ""),
    "player_mode": "system",
    "custom_player_path": "",
}