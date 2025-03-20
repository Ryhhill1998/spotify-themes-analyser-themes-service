from functools import lru_cache
from typing import Annotated

import aiosqlite
from fastapi import Depends, Request
from google import genai

from analysis_api.services.data_service import DataService
from analysis_api.services.model_service import ModelService
from analysis_api.services.storage.storage_service import StorageService
from analysis_api.settings import Settings


@lru_cache
def get_settings() -> Settings:
    """
    Retrieves the application settings.

    The settings are cached to optimize performance, ensuring they are only loaded once per application instance.

    Returns
    -------
    Settings
        The application settings instance.
    """

    return Settings()


SettingsDependency = Annotated[Settings, Depends(get_settings)]


def get_genai_client(request: Request) -> genai.Client:
    """
    Retrieves the GenAI client from the FastAPI application state.

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    genai.Client
        The GenAI client instance stored in the application state.
    """

    return request.app.state.genai_client


GenaiClientDependency = Annotated[genai.Client, Depends(get_genai_client)]


def get_model_prompt(request: Request) -> str:
    """
    Determines the appropriate model prompt based on the request path.

    The prompt is selected based on whether the request is for an emotional profile or emotional tags.

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    str
        The prompt template to be used for this route.

    Raises
    ------
    Exception
        If the request path does not match expected endpoints.
    """

    if "profile" in request.url.path:
        prompt = request.app.state.model_emotional_profile_prompt
    elif "tags" in request.url.path:
        prompt = request.app.state.model_emotional_tagging_prompt
    else:
        raise Exception("Invalid path")

    return prompt


ModelPromptDependency = Annotated[str, Depends(get_model_prompt)]


def get_model_service(
        settings: SettingsDependency,
        model_prompt: ModelPromptDependency,
        genai_client: GenaiClientDependency
) -> ModelService:
    """
    Creates and returns a ModelService instance.

    The model service is responsible for generating responses using a specified AI model.

    Parameters
    ----------
    settings : Settings
        The application settings instance.
    model_prompt : str
        The prompt for the model.
    genai_client : genai.Client
        The GenAI client used for interacting with the model.

    Returns
    -------
    ModelService
        The configured ModelService instance.
    """

    return ModelService(
        client=genai_client,
        model=settings.model_name,
        prompt_template=model_prompt,
        temp=settings.model_temp,
        top_p=settings.model_top_p,
        max_output_tokens=settings.model_max_output_tokens
    )


ModelServiceDependency = Annotated[ModelService, Depends(get_model_service)]


async def get_db_conn(settings: SettingsDependency):
    """Dependency to get an async database connection."""
    db = await aiosqlite.connect(settings.db_path)

    try:
        yield db  # Provide connection to route handlers
    finally:
        await db.close()


DBConnectionDependency = Annotated[aiosqlite.Connection, Depends(get_db_conn)]


def get_storage_service(db_conn: DBConnectionDependency) -> StorageService:
    """
    Retrieves the storage service from the FastAPI application state.

    Parameters
    ----------
    db_conn : DBConnectionDependency
        The connection to the database.

    Returns
    -------
    StorageService
        The configured StorageService instance.
    """

    return StorageService(db_conn)


StorageServiceDependency = Annotated[StorageService, Depends(get_storage_service)]


def get_data_service(model_service: ModelServiceDependency, storage_service: StorageServiceDependency) -> DataService:
    """
    Creates and returns a DataService instance.

    The data service manages interactions between the model and the storage service.

    Parameters
    ----------
    model_service : ModelService
        The model service instance responsible for generating responses.
    storage_service : StorageService
        The storage service instance responsible for persisting data.

    Returns
    -------
    DataService
        The configured DataService instance.
    """

    return DataService(model_service=model_service, storage_service=storage_service)


DataServiceDependency = Annotated[DataService, Depends(get_data_service)]
