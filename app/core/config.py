from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Luxe Solara Qualification"
    database_url: str = "sqlite+pysqlite:///./luxe.db"
    secret_key: str = "dev-only"
    cors_origins: str = "http://localhost:8000"
    ghl_api_key: str = ""
    ghl_location_id: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
