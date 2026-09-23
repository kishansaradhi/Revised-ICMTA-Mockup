
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings:
    app_name = os.getenv("APP_NAME", "ICMTA Backend API")
    database_url = os.getenv("DATABASE_URL", "")
    jwt_secret = os.getenv("JWT_SECRET", "")
    jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "480"))

    cors_origins = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8000,http://localhost:8000"
        ).split(",")
        if origin.strip()
    ]

    upload_dir = os.getenv(
        "UPLOAD_DIR",
        str(BASE_DIR / "uploads")
    )


settings = Settings()

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.upload_dir, "member_photos").mkdir(parents=True, exist_ok=True)
Path(settings.upload_dir, "event_posters").mkdir(parents=True, exist_ok=True)
Path(settings.upload_dir, "payment_proofs").mkdir(parents=True, exist_ok=True)
