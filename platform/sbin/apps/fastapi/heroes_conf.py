from pydantic import BaseSettings
from pathlib import Path


class Settings(BaseSettings):

    # General Settings
    NAMESPACE: str
    PROTOCOL: str
    FASTAPI_DIR: str

    # Database Settings
    DB_HOST: str
    DB_PORT: int
    DB_PASSWORD: str
    DB_USER: str
    DB_NAME: str

    SQLITE: bool

    # OKA Settings
    OKA_USERNAME: str
    OKA_PASSWORD: str
    OKA_NAMESPACE: str

    class Config:
        
        env_file = f"{Path(__file__).resolve().parent}/.env"
        env_file_encoding = 'utf-8'


settings = Settings()
