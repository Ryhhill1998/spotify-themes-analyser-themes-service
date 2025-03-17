from fastapi import APIRouter

from analysis_api.dependencies import DataServiceDependency
from analysis_api.models import EmotionalProfileRequest, EmotionalTagsRequest, EmotionalTagsResponse, \
    EmotionalProfileResponse

router = APIRouter(prefix="/emotions")


@router.post("/emotional-profile")
async def get_emotional_profile(
        request: EmotionalProfileRequest,
        data_service: DataServiceDependency
) -> EmotionalProfileResponse:
    try:
        emotional_profile = await data_service.get_emotional_profile(request)
        return emotional_profile
    except Exception as e:
        print(e)
        raise


@router.post("/emotional-tags")
async def get_emotional_tags(
        request: EmotionalTagsRequest,
        data_service: DataServiceDependency
) -> EmotionalTagsResponse:
    try:
        emotional_tags = await data_service.get_emotional_tags(request)
        return emotional_tags
    except Exception as e:
        print(e)
        raise
