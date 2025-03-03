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


def get_model_service(request: Request) -> ModelService:
    return request.app.state.model_service


def get_storage_service(request: Request) -> StorageService:
    return request.app.state.storage_service


def get_data_service(
        model_service: Annotated[ModelService, Depends(get_model_service)],
        storage_service: Annotated[StorageService, Depends(get_storage_service)]
) -> DataService:
    return DataService(model_service=model_service, storage_service=storage_service)
