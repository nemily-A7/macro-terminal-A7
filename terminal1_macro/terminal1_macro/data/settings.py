from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env from the repo root regardless of the working directory
_env_file = Path(__file__).parents[3] / ".env"

class Settings(BaseSettings):
    db_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/terminal"

    # API Keys
    fred_api_key: str | None = None
    trading_economics_api_key: str | None = None
    massive_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=str(_env_file), extra="ignore")

settings = Settings()
