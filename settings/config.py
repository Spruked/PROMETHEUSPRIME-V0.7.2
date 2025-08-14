# settings/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Caleon 2.0 Core"
    debug: bool = True
    environment: str = "development"
    openai_api_key: str = ""
    allowed_hosts: list[str] = ["*"]

    class Config:
        env_file = ".env"
