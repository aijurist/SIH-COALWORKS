from pathlib import Path 
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    # VECTOR_DIR: str = "chatbot/vector_index"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    settings = Settings(_env_file=".env", _env_file_encoding="utf-8")
    # print(f"GOOGLE_API_KEY: {settings.GOOGLE_API_KEY}")
    return settings