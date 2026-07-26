from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Sistema de Gestion de Inventario"
    app_env: str = "development"
    database_url: str


settings = Settings()
