from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 7
    GOOGLE_API_KEY: str
    BREVO_API_KEY: str = ""
    BREVO_SENDER_EMAIL: str = "noreply@idaraty.tn"
    BREVO_SENDER_NAME: str = "iDaraty"
    BREVO_SMS_SENDER: str = "iDaraty"
    APP_NAME: str = "iDaraty"
    APP_URL: str = "http://localhost:5173"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()