from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_url: str = "postgresql+psycopg://postgres:postgres@localhost:5433/terminal"
    
    # API Keys
    fred_api_key: str | None = None
    trading_economics_api_key: str | None = None
    massive_api_key: str | None = None
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
