from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request

from analysis_api.services.data_service import DataService
from analysis_api.services.model_service import ModelService
from analysis_api.services.storage_service import StorageService
from analysis_api.settings import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_model_service(request: Request, settings: Annotated[Settings, Depends(get_settings)]) -> ModelService:
    if "profile" in request.url.path:
        prompt = request.app.state.model_emotional_profile_prompt
    elif "tags":
        prompt = request.app.state.model_emotional_tagging_prompt

    return ModelService(
        project_id=settings.gcp_project_id,
        location=settings.gcp_location,
        model=settings.model_name,
        prompt_template=prompt,
        temp=settings.model_temp,
        top_p=settings.model_top_p,
        max_output_tokens=settings.model_max_output_tokens
    )


def get_storage_service(request: Request) -> StorageService:
    return request.app.state.storage_service


def get_data_service(
        model_service: Annotated[ModelService, Depends(get_model_service)],
        storage_service: Annotated[StorageService, Depends(get_storage_service)]
) -> DataService:
    return DataService(model_service=model_service, storage_service=storage_service)


DataServiceDependency = Annotated[DataService, Depends(get_data_service)]
