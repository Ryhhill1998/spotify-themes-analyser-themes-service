import sys
from contextlib import asynccontextmanager

import aiosqlite
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger
from google import genai

from analysis_api.services.storage.storage_service import initialise_db
from analysis_api.settings import Settings
from analysis_api.routers import emotions


def initialise_logger():
    logger.remove()
    logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")
    logger.add(sys.stderr, format="{time} {level} {message}", level="ERROR")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()

    initialise_logger()

    # initialise database
    db = await aiosqlite.connect(settings.db_path)
    await initialise_db(db)
    await db.close()

    # initialise prompts
    prompts_path = settings.model_prompts_path

    with open(prompts_path / settings.model_emotional_profile_prompt_file_name) as emotional_profile_prompt_file:
        app.state.model_emotional_profile_prompt = emotional_profile_prompt_file.read()

    with open(prompts_path / settings.model_emotional_tagging_prompt_file_name) as emotional_tagging_prompt_file:
        app.state.model_emotional_tagging_prompt = emotional_tagging_prompt_file.read()

    # initialise genai client
    app.state.genai_client = genai.Client(
        vertexai=True,
        project=settings.gcp_project_id,
        location=settings.gcp_location
    )

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def health_check():
    return {"status": "running"}


app.include_router(emotions.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, e: Exception):
    """Handles all unhandled exceptions globally."""
    logger.exception(f"Unhandled Exception occurred at {request.url} - {e}")

    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please try again later."},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all incoming requests."""

    ip_addr = request.client.host
    port = request.client.port
    url = request.url
    req_method = request.method

    log_message = f"{ip_addr}:{port} made {req_method} request to {url}."

    logger.info(log_message)

    response = await call_next(request)
    return response
