"""Application configuration."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "HR Resume Screening System"
    database_url: str = "sqlite:///./hr_system.db"
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 10
    supported_formats: list[str] = [".pdf", ".docx"]
    top_candidates_default: int = 10

    model_config = {"env_prefix": "HR_"}

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
