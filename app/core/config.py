from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Taster"
    VERSION: str = "0.1.0"
    ENV: str = "dev"

    DATABASE_URL: str = "sqlite:///./taster.db"
    AUTO_CREATE_TABLES: bool = True
    LOG_LEVEL: str = "INFO"

    #JWT 토큰 키
    JWT_SECRET: str = "change-me"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
