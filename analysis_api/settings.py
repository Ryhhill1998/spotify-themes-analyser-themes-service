from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gcp_project_id: str
    gcp_location: str

    model_name: str
    model_temp: float
    model_top_p: float
    model_max_output_tokens: int
    model_prompt_path: Path

    redis_host: str
    redis_port: int

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
