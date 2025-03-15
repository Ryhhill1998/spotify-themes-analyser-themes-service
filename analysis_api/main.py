from contextlib import asynccontextmanager
from typing import Annotated

import redis.asyncio as redis
from fastapi import FastAPI, Depends

from analysis_api.dependencies import get_data_service
from analysis_api.models import AnalysisRequest, EmotionalProfileResponse, EmotionalTagsResponse
from analysis_api.services.data_service import DataService
from analysis_api.services.storage_service import StorageService
from analysis_api.settings import Settings


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
        yield
    finally:
        await redis_client.aclose()


app = FastAPI(lifespan=lifespan)


@app.post("/emotional-profile")
async def get_emotional_profile(
        analysis_request: AnalysisRequest,
        data_service: Annotated[DataService, Depends(get_data_service)]
) -> EmotionalProfileResponse:
    try:
        emotional_profile = await data_service.get_emotional_profile(analysis_request)
        return emotional_profile
    except Exception as e:
        print(e)
        raise


@app.post("/emotional-tags")
async def get_emotional_tags(
        analysis_request: AnalysisRequest,
        data_service: Annotated[DataService, Depends(get_data_service)]
) -> EmotionalTagsResponse:
    try:
        emotional_tags = await data_service.get_emotional_tags(analysis_request)
        return emotional_tags
    except Exception as e:
        print(e)
        raise
