from contextlib import asynccontextmanager
from typing import Annotated

import redis.asyncio as redis
from fastapi import FastAPI, Depends

from analysis_api.dependencies import get_data_service
from analysis_api.models import AnalysisRequest, AnalysisResponse
from analysis_api.services.data_service import DataService
from analysis_api.services.model_service import ModelService
from analysis_api.services.storage_service import StorageService
from analysis_api.settings import Settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()

    with open(settings.model_prompt_path) as model_prompt_file:
        model_prompt = model_prompt_file.read()

    app.state.model_service = ModelService(
        project_id=settings.gcp_project_id,
        location=settings.gcp_location,
        model=settings.model_name,
        prompt_template=model_prompt,
        temp=settings.model_temp,
        top_p=settings.model_top_p,
        max_output_tokens=settings.model_max_output_tokens
    )

    redis_client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

    try:
        app.state.storage_service = StorageService(redis_client)

        yield
    finally:
        await redis_client.aclose()


app = FastAPI(lifespan=lifespan)


@app.post("/emotional-profile")
async def get_emotional_profile(
        analysis_requests: list[AnalysisRequest],
        data_service: Annotated[DataService, Depends(get_data_service)]
) -> list[AnalysisResponse]:
    try:
        analysis_response_list = await data_service.get_emotional_analysis_list(analysis_requests)
        return analysis_response_list
    except Exception as e:
        print(e)
