import asyncio
import json

from analysis_api.models import AnalysisRequest, EmotionalProfile, EmotionalProfileResponse, EmotionalTagsResponse
from analysis_api.services.model_service import ModelService
from analysis_api.services.storage_service import StorageService


class DataService:
    def __init__(self, model_service: ModelService, storage_service: StorageService):
        self.model_service = model_service
        self.storage_service = storage_service

    async def get_emotional_profile(self, analysis_request: AnalysisRequest) -> EmotionalProfileResponse:
        track_id = analysis_request.track_id
        lyrics = analysis_request.lyrics
        storage_key = f"{track_id}_profile"

        item = await self.storage_service.retrieve_item(storage_key)

        if item is not None:
            json_data = json.loads(item)
        else:
            data = await asyncio.to_thread(self.model_service.generate_response, lyrics)
            json_data = json.loads(data)
            await self.storage_service.store_item(key=storage_key, value=json.dumps(json_data))

        emotional_profile = EmotionalProfile(**json_data)
        analysis_response = EmotionalProfileResponse(track_id=track_id, emotional_profile=emotional_profile, lyrics=lyrics)

        return analysis_response


    async def get_emotional_tags(self, analysis_request: AnalysisRequest) -> EmotionalTagsResponse:
        track_id = analysis_request.track_id
        storage_key = f"{track_id}_tags"

        data = await self.storage_service.retrieve_item(storage_key)

        if data is None:
            data = await asyncio.to_thread(self.model_service.generate_response, analysis_request.lyrics)
            data = data.replace("\\", "")
            await self.storage_service.store_item(key=storage_key, value=data)

        emotional_tagging_response = EmotionalTagsResponse(track_id=track_id, lyrics=data)

        return emotional_tagging_response
