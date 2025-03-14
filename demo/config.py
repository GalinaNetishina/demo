from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path


class Settings(BaseSettings):
    MODE: str = 'dev'
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    POSTGRES_PASSWORD: str
    SMTP_USER: str
    SMTP_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int
    FRONTEND_HOST: str
    FRONTEND_PORT: int

    model_config = SettingsConfigDict(env_file=os.path.join(Path.cwd(), ".env-non-dev"))

    @property
    def DSN_postgresql_psycopg(self) -> str:
        # return "postgresql+psycopg2://postgres:postgres@localhost:10000/demo"  
        return "postgresql+psycopg2://postgres:postgres@db:5435/postgres"        

    @property
    def DSN_postgresql_asyncpg(self) -> str:
        
        if self.MODE == 'dev':
            return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:"
            f"{self.DB_PASS}"
            f"@{self.DB_HOST}:"
            f"{self.DB_PORT}/"
            f"{self.DB_NAME}"
        )
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:"
            f"{self.DB_PASS}"
            f"@localhost:"
            f"{self.DB_PORT}/"
            f"test_db"
        )

    @property
    def TEST_DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.DB_USER}:"
            f"{self.DB_PASS}"
            f"@localhost:"
            f"{self.DB_PORT}/"
            f"test_db"
        )


settings = Settings()
