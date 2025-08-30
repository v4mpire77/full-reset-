from pathlib import Path

class Settings:
    STORAGE_DIR = Path(__file__).parent.parent / "storage"
    MAX_UPLOAD_MB = 10

settings = Settings()

# Create storage directory if it doesn't exist
settings.STORAGE_DIR.mkdir(exist_ok=True)
