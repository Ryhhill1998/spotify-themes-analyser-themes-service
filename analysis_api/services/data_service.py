import asyncio
import json

from analysis_api.models import AnalysisRequest, EmotionalAnalysis, EmotionalProfile
from analysis_api.services.model_service import ModelService
from analysis_api.services.storage_service import StorageService


class DataService:
    def __init__(self, model_service: ModelService, storage_service: StorageService):
        self.model_service = model_service
        self.storage_service = storage_service

    async def _get_track_emotional_analysis(self, track_id: str, lyrics: str) -> EmotionalAnalysis:
        item = await self.storage_service.retrieve_item(track_id)

        if item is not None:
            data = json.loads(item)
        else:
            data = await asyncio.to_thread(self.model_service.generate_response, lyrics)
            await self.storage_service.store_item(key=track_id, value=json.dumps(data))

        emotional_profile = EmotionalAnalysis(**data)

        return emotional_profile

    async def _get_track_emotional_profile(self, track_id: str, lyrics: str) -> EmotionalProfile:
        emotional_profile = await self._get_track_emotional_analysis(track_id=track_id, lyrics=lyrics)

        emotional_profile_response = EmotionalProfile(
            track_id=track_id,
            lyrics=lyrics,
            emotional_analysis=emotional_profile
        )

        return emotional_profile_response

    async def get_emotional_profiles(self, analysis_requests: list[AnalysisRequest]) -> list[EmotionalProfile]:
        tasks = [
            self._get_track_emotional_profile(
                track_id=req.track_id,
                lyrics=req.lyrics
            )
            for req
            in analysis_requests
        ]

        emotional_profiles = await asyncio.gather(*tasks, return_exceptions=True)
        successful_results = [item for item in emotional_profiles if isinstance(item, EmotionalProfile)]

        return successful_results
