from contextlib import asynccontextmanager
from fastapi import FastAPI
from google import genai

from analysis_api.services.storage.storage_service import initialise_db
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

    app.state.genai_client = genai.Client(
        vertexai=True,
        project=settings.gcp_project_id,
        location=settings.gcp_location
    )

    # initialise database
    await initialise_db(settings.db_path)

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def health_check():
    return {"status": "running"}


app.include_router(emotions.router)
