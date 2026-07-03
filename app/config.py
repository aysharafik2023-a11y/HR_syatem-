from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "HR System API"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/hr_system"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: list[str] = ["*"]

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
