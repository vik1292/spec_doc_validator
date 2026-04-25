from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SPECVAL_", env_file=".env")

    anthropic_api_key: str | None = None
    registry_path: Path = Path.home() / ".config" / "specval" / "registry.json"
    model: str = "claude-sonnet-4-6"
    max_sample_rows: int = 20
    max_unique_values: int = 20


settings = Settings()
