from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str
    APP_ENV: str
    SECRET_KEY: str
    DATABASE_URL: str
    SESSION_COOKIE_NAME: str
    SESSION_EXPIRE_DAYS: int
    GEMINI_API_KEY: str
    OPENAI_API_KEY: str


settings = Settings()