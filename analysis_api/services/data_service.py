import asyncio
import json

import pydantic

from analysis_api.models import EmotionalProfile, EmotionalProfileResponse, EmotionalTagsResponse, \
    EmotionalProfileRequest, EmotionalTagsRequest
from analysis_api.services.model_service import ModelService, ModelServiceException
from analysis_api.services.storage_service import StorageService, StorageServiceException


class DataServiceException(Exception):
    """Base exception for errors encountered in the DataService."""

    def __init__(self, message: str):
        super().__init__(message)


class DataService:
    def __init__(self, model_service: ModelService, storage_service: StorageService):
        self.model_service = model_service
        self.storage_service = storage_service

    async def _get_emotional_profile_data(self, track_id: str, lyrics: str) -> dict[str, float]:
        storage_key = f"{track_id}_profile"

        item = await self.storage_service.retrieve_item(storage_key)

        if item is not None:
            emotional_profile_data = json.loads(item)
        else:
            data = await asyncio.to_thread(self.model_service.generate_response, lyrics)
            await self.storage_service.store_item(key=storage_key, value=data)
            emotional_profile_data = json.loads(data)

        return emotional_profile_data

    async def get_emotional_profile(self, request: EmotionalProfileRequest) -> EmotionalProfileResponse:
        track_id = request.track_id
        lyrics = request.lyrics

        try:
            emotional_profile_data = await self._get_emotional_profile_data(track_id=track_id, lyrics=lyrics)

            emotional_profile = EmotionalProfile(**emotional_profile_data)
            analysis_response = EmotionalProfileResponse(
                track_id=track_id,
                emotional_profile=emotional_profile,
                lyrics=lyrics
            )

            return analysis_response
        except (ModelServiceException, StorageServiceException) as e:
            message = f"Failed to retrieve emotional profile for track_id: {track_id}, lyrics: {lyrics} - {e}"
            print(message)
            raise DataServiceException(message)
        except pydantic.ValidationError as e:
            message = f"Failed to create EmotionalProfileResponse object - {e}"
            print(message)
            raise DataServiceException(message)

    async def _get_emotional_tags_data(self, track_id: str, lyrics: str, emotion: str) -> str:
        storage_key = f"{track_id}_tags_{emotion}"

        emotional_tags_data = await self.storage_service.retrieve_item(storage_key)

        if emotional_tags_data is None:
            model_input = f"\nEmotion to Tag: {emotion}\nLyrics: {lyrics}"
            emotional_tags_data = await asyncio.to_thread(self.model_service.generate_response, model_input)
            emotional_tags_data = emotional_tags_data.replace("\\", "")
            await self.storage_service.store_item(key=storage_key, value=emotional_tags_data)

        return emotional_tags_data

    async def get_emotional_tags(self, request: EmotionalTagsRequest) -> EmotionalTagsResponse:
        track_id = request.track_id
        lyrics = request.lyrics
        emotion = request.emotion

        try:
            emotional_tags_data = await self._get_emotional_tags_data(track_id=track_id, lyrics=lyrics, emotion=emotion)

            emotional_tagging_response = EmotionalTagsResponse(
                track_id=track_id,
                emotion=emotion,
                lyrics=emotional_tags_data
            )

            return emotional_tagging_response
        except (ModelServiceException, StorageServiceException) as e:
            message = (
                f"Failed to retrieve emotional profile for track_id: {track_id}, lyrics: {lyrics}, "
                f"emotion: {emotion} - {e}"
            )
            print(message)
            raise DataServiceException(message)
        except pydantic.ValidationError as e:
            message = f"Failed to create EmotionalTagsResponse object - {e}"
            print(message)
            raise DataServiceException(message)
