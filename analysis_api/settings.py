from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gcp_project_id: str
    gcp_location: str

    model_name: str
    model_temp: float
    model_top_p: float
    model_max_output_tokens: int

    model_prompts_path: Path
    model_emotional_profile_prompt_file_name: str
    model_emotional_tagging_prompt_file_name: str

    db_path: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
