import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    port: int = 8080
    ocr_confidence_threshold: int = 60
    cache_max_size: int = 1000
    batch_timeout_seconds: int = 300
    max_batch_size: int = 50

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
