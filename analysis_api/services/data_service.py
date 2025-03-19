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
    """
    Service for processing emotional analysis of song lyrics.

    This service interacts with a machine learning model to generate emotional profiles and emotional tags for song
    lyrics. It also utilises a storage service to store results, reducing redundant calls to the model

    Attributes
    ----------
    model_service : ModelService
        The service responsible for interacting with the machine learning model.
    storage_service : StorageService
        The service responsible for storing and retrieving previously stored results return by the model.

    Methods
    -------
    get_emotional_profile(request: EmotionalProfileRequest) -> EmotionalProfileResponse
        Retrieves the emotional profile for a given track based on its lyrics.
        If the data exists in storage, it is retrieved; otherwise, it is generated using the model.

    get_emotional_tags(request: EmotionalTagsRequest) -> EmotionalTagsResponse
        Retrieves emotional tags for a given track based on a specific emotion.
        If the data exists in storage, it is retrieved; otherwise, it is generated using the model.
    """

    def __init__(self, model_service: ModelService, storage_service: StorageService):
        """
        Parameters
        ----------
        model_service : ModelService
            Instance of ModelService to handle generating and retrieving responses from the model.
        storage_service : StorageService
            Instance of StorageService to manage data storage.
        """

        self.model_service = model_service
        self.storage_service = storage_service

    async def _get_emotional_profile_data(self, track_id: str, lyrics: str) -> dict[str, float]:
        """
        Retrieves or generates the emotional profile data for a given track.

        If the data exists in storage, it is retrieved; otherwise, it is generated using the model and stored for future
        use.

        Parameters
        ----------
        track_id : str
            The unique identifier for the track.
        lyrics : str
            The lyrics of the song to analyze.

        Returns
        -------
        dict[str, float]
            A dictionary representing the track's emotional profile, where each key is an emotion and each value is the
            proportion of the lyrics associated with that emotion.


        Raises
        ------
        StorageServiceException
            If there is an issue retrieving or storing data.
        ModelServiceException
            If there is an issue generating a response from the model.
        """

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
        """
        Retrieves the emotional profile for a given track based on its lyrics.

        The emotional profile is either retrieved from storage or generated using the model.

        Parameters
        ----------
        request : EmotionalProfileRequest
            Request object containing track ID and lyrics.

        Returns
        -------
        EmotionalProfileResponse
            Response object containing the emotional profile.

        Raises
        ------
        DataServiceException
            If an error occurs during retrieval, processing, or validation.
        """

        track_id = request.track_id
        lyrics = request.lyrics

        try:
            emotional_profile_data = await self._get_emotional_profile_data(track_id=track_id, lyrics=lyrics)

            emotional_profile = EmotionalProfile(**emotional_profile_data)
            emotional_profile_response = EmotionalProfileResponse(
                track_id=track_id,
                emotional_profile=emotional_profile,
                lyrics=lyrics
            )

            return emotional_profile_response
        except (ModelServiceException, StorageServiceException) as e:
            message = f"Failed to retrieve emotional profile for track_id: {track_id}, lyrics: {lyrics} - {e}"
            print(message)
            raise DataServiceException(message)
        except pydantic.ValidationError as e:
            message = f"Failed to create EmotionalProfileResponse object - {e}"
            print(message)
            raise DataServiceException(message)

    async def _get_emotional_tags_data(self, track_id: str, lyrics: str, emotion: str) -> str:
        """
        Retrieves or generates emotional tags for a given track based on a specific emotion.

        If the data exists in storage, it is retrieved; otherwise, it is generated using the model and stored for future
        use.

        Parameters
        ----------
        track_id : str
            The unique identifier for the track.
        lyrics : str
            The lyrics of the song to analyze.
        emotion : str
            The emotion for which tags should be generated.

        Returns
        -------
        str
            The original lyrics with certain phrases wrapped in <span> tags, where the class names correspond to the
            detected emotion.

        Raises
        ------
        StorageServiceException
            If there is an issue retrieving or storing data.
        ModelServiceException
            If there is an issue generating a response from the model.
        """

        storage_key = f"{track_id}_tags_{emotion}"

        emotional_tags_data = await self.storage_service.retrieve_item(storage_key)

        if emotional_tags_data is None:
            model_input = f"\nEmotion to Tag: {emotion}\nLyrics: {lyrics}"
            emotional_tags_data = await asyncio.to_thread(self.model_service.generate_response, model_input)
            emotional_tags_data = emotional_tags_data.replace("\\", "")
            await self.storage_service.store_item(key=storage_key, value=emotional_tags_data)

        return emotional_tags_data

    async def get_emotional_tags(self, request: EmotionalTagsRequest) -> EmotionalTagsResponse:
        """
        Retrieves emotional tags for a given track based on a specific emotion.

        The tags are either retrieved from storage or generated using the model.

        Parameters
        ----------
        request : EmotionalTagsRequest
            Request object containing track ID, lyrics, and emotion.

        Returns
        -------
        EmotionalTagsResponse
            Response object containing emotional tags.

        Raises
        ------
        DataServiceException
            If an error occurs during retrieval, processing, or validation.
        """

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
