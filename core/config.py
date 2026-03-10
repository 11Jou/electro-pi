from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
print(ENV_FILE)

class Settings(BaseSettings):
    DATABASE_URL: str = ""
    OPENAI_API_KEY: str = ""
    CHAT_BOT_SERVICE: str = "openai"
    MOCK: bool = False

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
    )


settings = Settings()
