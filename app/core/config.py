from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "OneStack Financial Parser"
    DATABASE_URL: str = "sqlite:///./financial_data.db"
    UPLOAD_DIR: str = "data/uploads"
    MAX_FILE_SIZE_MB: int = 10

    class Config:
        env_file = ".env"

settings = Settings()