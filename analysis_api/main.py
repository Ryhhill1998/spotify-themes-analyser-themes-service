from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi import FastAPI
from google import genai

from analysis_api.services.storage_service import StorageService
from analysis_api.settings import Settings
from analysis_api.routers import emotions


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()

    prompts_path = settings.model_prompts_path

    with open(prompts_path / settings.model_emotional_profile_prompt_file_name) as emotional_profile_prompt_file:
        app.state.model_emotional_profile_prompt = emotional_profile_prompt_file.read()

    with open(prompts_path / settings.model_emotional_tagging_prompt_file_name) as emotional_tagging_prompt_file:
        app.state.model_emotional_tagging_prompt = emotional_tagging_prompt_file.read()

    redis_client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

    try:
        app.state.storage_service = StorageService(redis_client)
        app.state.genai_client = genai.Client(vertexai=True, project=settings.project_id, location=settings.location)
        yield
    finally:
        await redis_client.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(emotions.router)
