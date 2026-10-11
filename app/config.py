from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    google_api_key: str
    google_model: str = "gemini-3.6-flash"
    database_url: str = "sqlite:///./data/job_matcher.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
