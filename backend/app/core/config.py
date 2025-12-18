from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Emo Finance API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:4200",
        "http://localhost",
        "http://frontend:4200"
    ]

    # MongoDB
    MONGO_URI: str = "mongodb://mongodb:27017"
    MONGO_DB_NAME: str = "emo_finance"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
