import asyncio
import threading

from analysis_api.models import AnalysisRequest, EmotionalProfile, AnalysisResponse
from analysis_api.services.model_service import ModelService
from analysis_api.services.storage_service import StorageService


class DataService:
    def __init__(self, model_service: ModelService, storage_service: StorageService):
        self.model_service = model_service
        self.storage_service = storage_service

    async def _get_emotional_profile(self, lyrics: str) -> EmotionalProfile:
        data = await asyncio.to_thread(self.model_service.generate_response, lyrics)

        emotional_profile = EmotionalProfile(**data)

        return emotional_profile

    async def _get_analysis_response(self, analysis_request: AnalysisRequest) -> AnalysisResponse:
        emotional_profile = await self._get_emotional_profile(analysis_request.lyrics)

        analysis_response = AnalysisResponse(**analysis_request.dict(), emotional_profile=emotional_profile)

        return analysis_response

    async def get_analysis_response_list(self, analysis_requests: list[AnalysisRequest]) -> list[AnalysisResponse]:
        tasks = [self._get_analysis_response(req) for req in analysis_requests]

        analysis_response_list = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = [item for item in analysis_response_list if not isinstance(item, Exception)]
        failed_count = len(analysis_response_list) - len(successful_results)
        print(f"Success: {len(successful_results)}")

        # Ensure at least 50% success rate
        if len(successful_results) >= len(analysis_response_list) // 2:
            return successful_results
        else:
            raise RuntimeError(f"Too many failures! Only {len(successful_results)} succeeded, {failed_count} failed.")
