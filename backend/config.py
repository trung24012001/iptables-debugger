import pathlib
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
