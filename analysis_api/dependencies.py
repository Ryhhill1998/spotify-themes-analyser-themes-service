from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request
from google import genai

from analysis_api.services.data_service import DataService
from analysis_api.services.model_service import ModelService
from analysis_api.services.storage_service import StorageService
from analysis_api.settings import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_genai_client(request: Request) -> genai.Client:
    return request.app.state.genai_client


def get_model_config(request: Request, settings: Annotated[Settings, Depends(get_settings)]) -> tuple[str, str, str]:
    if "profile" in request.url.path:
        prompt = request.app.state.model_emotional_profile_prompt
        response_type = settings.model_emotional_profile_response_type
        response_mime_type = settings.model_emotional_profile_response_mime_type
    elif "tags" in request.url.path:
        prompt = request.app.state.model_emotional_tagging_prompt
        response_type = settings.model_emotional_tagging_response_type
        response_mime_type = settings.model_emotional_tagging_response_mime_type
    else:
        raise Exception("Invalid path")

    return prompt, response_type, response_mime_type


def get_model_service(
        settings: Annotated[Settings, Depends(get_settings)],
        model_config: Annotated[tuple[str, str, str], Depends(get_model_config)],
        genai_client: Annotated[genai.Client, Depends(get_genai_client)]
) -> ModelService:
    prompt, response_type, response_mime_type = model_config

    return ModelService(
        client=genai_client,
        model=settings.model_name,
        prompt_template=prompt,
        temp=settings.model_temp,
        response_type=response_type,
        response_mime_type=response_mime_type,
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
