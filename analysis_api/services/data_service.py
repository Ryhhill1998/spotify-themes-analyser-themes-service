import asyncio
import json

from analysis_api.models import EmotionalProfile, EmotionalProfileResponse, EmotionalTagsResponse, \
    EmotionalProfileRequest, EmotionalTagsRequest
from analysis_api.services.model_service import ModelService
from analysis_api.services.storage_service import StorageService


class DataService:
    def __init__(self, model_service: ModelService, storage_service: StorageService):
        self.model_service = model_service
        self.storage_service = storage_service

    async def get_emotional_profile(self, request: EmotionalProfileRequest) -> EmotionalProfileResponse:
        track_id = request.track_id
        lyrics = request.lyrics

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


    async def get_emotional_tags(self, request: EmotionalTagsRequest) -> EmotionalTagsResponse:
        track_id = request.track_id
        emotion = request.emotion

        storage_key = f"{track_id}_tags_{emotion}"

        data = await self.storage_service.retrieve_item(storage_key)

        if data is None:
            model_input = f"\nEmotion to Tag: {emotion}\nLyrics: {request.lyrics}"
            data = await asyncio.to_thread(self.model_service.generate_response, model_input)
            data = data.replace("\\", "")
            await self.storage_service.store_item(key=storage_key, value=data)

        emotional_tagging_response = EmotionalTagsResponse(track_id=track_id, emotion=emotion, lyrics=data)

        return emotional_tagging_response
