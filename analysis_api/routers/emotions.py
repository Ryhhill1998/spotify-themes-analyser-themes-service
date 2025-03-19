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
    """
    Retrieves the emotional profile of a given track.

    The emotional profile consists of 15 emotions, each with a proportion between 0 and 1. These proportions indicate
    the percentage of the lyrics associated with each emotion. The sum of all emotion proportions is always equal to 1.

    Parameters
    ----------
    request : EmotionalProfileRequest
        The request containing the track ID and lyrics to analyze.
    data_service : DataServiceDependency
        The data service dependency responsible for retrieving the emotional profile.

    Returns
    -------
    EmotionalProfileResponse
        The emotional profile of the track, including emotion proportions.

    Raises
    ------
    HTTPException
        If a DataServiceException occurs, a 500 error is raised.
    """

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
    """
    Retrieves emotional tags for the lyrics of a given track based on a specified emotion.

    The emotional tags highlight phrases in the lyrics that correspond to the given emotion by surrounding them with
    span tags.

    Parameters
    ----------
    request : EmotionalTagsRequest
       The request containing the track ID, lyrics, and the emotion to analyze.
    data_service : DataServiceDependency
       The data service dependency responsible for retrieving or generating the emotional tags.

    Returns
    -------
    EmotionalTagsResponse
       A response containing the emotional tags applied to the lyrics.

    Raises
    ------
    HTTPException
       If a DataServiceException occurs, a 500 error is raised.
    """

    try:
        emotional_tags = await data_service.get_emotional_tags(request)
        return emotional_tags
    except DataServiceException as e:
        print(e)
        raise HTTPException(status_code=500, detail="Something went wrong")
