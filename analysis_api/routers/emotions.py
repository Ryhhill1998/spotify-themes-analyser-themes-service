from fastapi import APIRouter, HTTPException

from analysis_api.dependencies import DataServiceDependency
from analysis_api.models import EmotionalProfileRequest, EmotionalTagsRequest, EmotionalTagsResponse, \
    EmotionalProfileResponse
from analysis_api.services.data_service import DataServiceException

router = APIRouter(prefix="/emotions")


@router.post("/profile")
async def get_emotional_profile(
        request: EmotionalProfileRequest,
        data_service: DataServiceDependency
) -> EmotionalProfileResponse:
    try:
        emotional_profile = await data_service.get_emotional_profile(request)
        return emotional_profile
    except DataServiceException as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.post("/tags")
async def get_emotional_tags(
        request: EmotionalTagsRequest,
        data_service: DataServiceDependency
) -> EmotionalTagsResponse:
    try:
        emotional_tags = await data_service.get_emotional_tags(request)
        return emotional_tags
    except DataServiceException as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong")
