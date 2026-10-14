from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AutoAssist API"
    database_url: str = "sqlite:///./autoassist.db"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    escalation_threshold: float = 0.72
    knowledge_dir: str = "/app/knowledge"


@lru_cache
def get_settings() -> Settings:
    return Settings()
