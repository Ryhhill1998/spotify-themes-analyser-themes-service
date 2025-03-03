from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends

from analysis_api.dependencies import get_data_service
from analysis_api.models import AnalysisRequest, EmotionalProfile
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

    app.state.storage_service = StorageService()

    yield


app = FastAPI(lifespan=lifespan)


@app.post("/emotional-profile")
def get_emotional_profile(
        analysis_requests: list[AnalysisRequest],
        data_service: Annotated[DataService, Depends(get_data_service)]
) -> EmotionalProfile:
    emotional_profile = data_service.get_emotional_profile(analysis_requests)

    return emotional_profile
