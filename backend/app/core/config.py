from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ChaosBrain AI"
    database_url: str = "sqlite:///./chaosbrain.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    @property
    def cors_origin_list(self) -> List[str]:
        defaults = ["http://localhost:5173", "http://127.0.0.1:5173"]
        items = [o.strip().rstrip("/") for o in self.cors_origins.split(",") if o.strip()]
        for d in defaults:
            if d not in items:
                items.append(d)
        return items


settings = Settings()
