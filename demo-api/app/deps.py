import os
from functools import lru_cache


class Settings:
    app_name: str = "Homelab Demo API"
    env: str
    version: str

    def __init__(self) -> None:
        self.env = os.getenv("APP_ENV", "dev")
        self.version = os.getenv("APP_VERSION", "unknown")


@lru_cache
def get_settings() -> Settings:
    return Settings()
