from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AutoAssist API"
    database_url: str = "sqlite:///./autoassist.db"
    llm_api_key: str = ""
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "meta-llama/llama-4-maverick"
    llm_temperature: float = 0.2
    llm_max_tokens: int = 700
    llm_app_url: str = "http://localhost:3000"
    llm_app_name: str = "AutoAssist DINAMEX PoC"
    escalation_threshold: float = 0.72
    knowledge_dir: str = "/app/knowledge"


@lru_cache
def get_settings() -> Settings:
    return Settings()
