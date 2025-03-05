import asyncio
import json

from analysis_api.models import AnalysisRequest, EmotionalProfile, AnalysisResponse
from analysis_api.services.model_service import ModelService
from analysis_api.services.storage_service import StorageService


class DataService:
    def __init__(self, model_service: ModelService, storage_service: StorageService):
        self.model_service = model_service
        self.storage_service = storage_service

    async def _get_emotional_profile(self, track_id: str, lyrics: str) -> EmotionalProfile:
        item = await self.storage_service.retrieve_item(track_id)

        if item is not None:
            data = json.loads(item)
        else:
            data = await asyncio.to_thread(self.model_service.generate_response, lyrics)
            await self.storage_service.store_item(key=track_id, value=json.dumps(data))

        emotional_profile = EmotionalProfile(**data)

        return emotional_profile

    async def _get_emotional_analysis(self, track_id: str, lyrics: str) -> AnalysisResponse:
        emotional_profile = await self._get_emotional_profile(track_id=track_id, lyrics=lyrics)

        analysis_response = AnalysisResponse(track_id=track_id, lyrics=lyrics, emotional_profile=emotional_profile)

        return analysis_response

    async def get_emotional_analysis_list(self, analysis_requests: list[AnalysisRequest]) -> list[AnalysisResponse]:
        tasks = [self._get_emotional_analysis(track_id=req.track_id, lyrics=req.lyrics) for req in analysis_requests]

        analysis_response_list = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = [item for item in analysis_response_list if not isinstance(item, Exception)]
        failed_count = len(analysis_response_list) - len(successful_results)
        print(f"Success: {len(successful_results)}")

        # Ensure at least 50% success rate
        if len(successful_results) >= len(analysis_response_list) // 2:
            return successful_results
        else:
            raise RuntimeError(f"Too many failures! Only {len(successful_results)} succeeded, {failed_count} failed.")
