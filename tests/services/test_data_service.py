import json
from unittest.mock import AsyncMock, Mock

import pytest

from analysis_api.models import EmotionalProfileRequest, EmotionalProfileResponse, EmotionalProfile, \
    EmotionalTagsRequest, Emotion, EmotionalTagsResponse
from analysis_api.services.data_service import DataService, DataServiceException
from analysis_api.services.model_service import ModelService, ModelServiceException
from analysis_api.services.storage_service import StorageService, StorageServiceException


@pytest.fixture
def mock_model_service() -> Mock:
    return AsyncMock(spec=ModelService)


@pytest.fixture
def mock_storage_service() -> Mock:
    return AsyncMock(spec=StorageService)


@pytest.fixture
def data_service(mock_model_service, mock_storage_service) -> DataService:
    return DataService(model_service=mock_model_service, storage_service=mock_storage_service)


# -------------------- EMOTIONAL PROFILE -------------------- #
@pytest.fixture
def mock_emotional_profile_data() -> dict[str, float]:
    return {
        "joy": 0.1,
        "sadness": 0.1,
        "anger": 0.2,
        "fear": 0.05,
        "love": 0.1,
        "hope": 0,
        "nostalgia": 0.03,
        "loneliness": 0.02,
        "confidence": 0.1,
        "despair": 0.15,
        "excitement": 0.1,
        "mystery": 0,
        "defiance": 0.05,
        "gratitude": 0.1,
        "spirituality": 0
    }


@pytest.fixture
def mock_emotional_profile_request() -> EmotionalProfileRequest:
    return EmotionalProfileRequest(track_id="1", lyrics="Lyrics for track 1")


# 1. Test that _get_emotional_profile_data does not call model if data in storage.
@pytest.mark.asyncio
async def test__get_emotional_profile_data_data_in_storage(
        data_service,
        mock_model_service,
        mock_storage_service,
        mock_emotional_profile_data
):
    mock_retrieve_item = AsyncMock()
    mock_retrieve_item.return_value = json.dumps(mock_emotional_profile_data)
    mock_storage_service.retrieve_item = mock_retrieve_item

    data = await data_service._get_emotional_profile_data(track_id="1", lyrics="Lyrics for track 1")

    assert data == mock_emotional_profile_data
    mock_storage_service.retrieve_item.assert_called_once_with("1_profile")
    mock_model_service.generate_response.assert_not_called()


# 2. Test that _get_emotional_profile_data calls model if data not in storage.
@pytest.mark.asyncio
async def test__get_emotional_profile_data_data_not_in_storage(
        data_service,
        mock_model_service,
        mock_storage_service,
        mock_emotional_profile_data
):
    mock_retrieve_item = AsyncMock()
    mock_retrieve_item.return_value = None
    mock_storage_service.retrieve_item = mock_retrieve_item
    mock_generate_response = Mock()
    json_string = json.dumps(mock_emotional_profile_data)
    mock_generate_response.return_value = json_string
    mock_model_service.generate_response = mock_generate_response
    lyrics = "Lyrics for track 1"

    data = await data_service._get_emotional_profile_data(track_id="1", lyrics=lyrics)

    assert data == mock_emotional_profile_data
    mock_storage_service.retrieve_item.assert_called_once_with("1_profile")
    mock_model_service.generate_response.assert_called_once_with(lyrics)
    mock_storage_service.store_item.assert_called_once_with(key="1_profile", value=json_string)


# 3. Test that get_emotional_profile raises a DataServiceException if a StorageServiceException occurs.
@pytest.mark.asyncio
async def test_get_emotional_profile_storage_failure(data_service, mock_emotional_profile_request):
    mock__get_emotional_profile_data = AsyncMock()
    mock__get_emotional_profile_data.side_effect = StorageServiceException("Test")
    data_service._get_emotional_profile_data = mock__get_emotional_profile_data

    with pytest.raises(
            DataServiceException,
            match=f"Failed to retrieve emotional profile for track_id: 1, lyrics: Lyrics for track 1"
    ):
        await data_service.get_emotional_profile(mock_emotional_profile_request)


# 4. Test that get_emotional_profile raises a DataServiceException if a ModelServiceException occurs.
@pytest.mark.asyncio
async def test_get_emotional_profile_model_failure(data_service, mock_emotional_profile_request):
    mock__get_emotional_profile_data = AsyncMock()
    mock__get_emotional_profile_data.side_effect = ModelServiceException("Test")
    data_service._get_emotional_profile_data = mock__get_emotional_profile_data

    with pytest.raises(
            DataServiceException,
            match=f"Failed to retrieve emotional profile for track_id: 1, lyrics: Lyrics for track 1"
    ):
        await data_service.get_emotional_profile(mock_emotional_profile_request)


# 5. Test that get_emotional_profile raises a DataServiceException if data validation fails.
@pytest.mark.parametrize(
    "missing_emotion",
    [
        "joy",
        "sadness",
        "anger",
        "fear",
        "love",
        "hope",
        "nostalgia",
        "loneliness",
        "confidence",
        "despair",
        "excitement",
        "mystery",
        "defiance",
        "gratitude",
        "spirituality"
    ]
)
@pytest.mark.asyncio
async def test_get_emotional_profile_data_validation_failure(
        data_service,
        mock_emotional_profile_request,
        mock_emotional_profile_data,
        missing_emotion
):
    mock__get_emotional_profile_data = AsyncMock()
    mock_emotional_profile_data.pop(missing_emotion)
    mock__get_emotional_profile_data.return_value = mock_emotional_profile_data
    data_service._get_emotional_profile_data = mock__get_emotional_profile_data

    with pytest.raises(DataServiceException, match="Failed to create EmotionalProfileResponse object"):
        await data_service.get_emotional_profile(mock_emotional_profile_request)


# 6. Test that get_emotional_profile returns expected emotional profile.
@pytest.mark.asyncio
async def test_get_emotional_profile_data_returns_expected_data(
        data_service,
        mock_emotional_profile_request,
        mock_emotional_profile_data
):
    mock__get_emotional_profile_data = AsyncMock()
    mock__get_emotional_profile_data.return_value = mock_emotional_profile_data
    data_service._get_emotional_profile_data = mock__get_emotional_profile_data

    res = await data_service.get_emotional_profile(mock_emotional_profile_request)

    assert res == EmotionalProfileResponse(
        track_id="1",
        lyrics="Lyrics for track 1",
        emotional_profile=EmotionalProfile(
            joy=0.1,
            sadness=0.1,
            anger=0.2,
            fear=0.05,
            love=0.1,
            hope=0,
            nostalgia=0.03,
            loneliness=0.02,
            confidence=0.1,
            despair=0.15,
            excitement=0.1,
            mystery=0,
            defiance=0.05,
            gratitude=0.1,
            spirituality=0
        )
    )

# -------------------- EMOTIONAL TAGS -------------------- #
@pytest.fixture
def mock_emotional_tags_data() -> str:
    return """<span class="anger">I’ll hurt you</span>"""


@pytest.fixture
def mock_emotional_tags_request() -> EmotionalTagsRequest:
    return EmotionalTagsRequest(track_id="1", lyrics="Lyrics for track 1", emotion=Emotion.JOY)


# 1. Test that _get_emotional_tags_data does not call model if data in storage.
@pytest.mark.asyncio
async def test__get_emotional_tags_data_data_in_storage(
        data_service,
        mock_model_service,
        mock_storage_service,
        mock_emotional_tags_data
):
    mock_retrieve_item = AsyncMock()
    mock_retrieve_item.return_value = mock_emotional_tags_data
    mock_storage_service.retrieve_item = mock_retrieve_item

    data = await data_service._get_emotional_tags_data(track_id="1", lyrics="Lyrics for track 1", emotion="joy")

    assert data == mock_emotional_tags_data
    mock_storage_service.retrieve_item.assert_called_once_with("1_tags_joy")
    mock_model_service.generate_response.assert_not_called()


# 2. Test that _get_emotional_tags_data calls model if data not in storage.
@pytest.mark.asyncio
async def test__get_emotional_tags_data_data_not_in_storage(
        data_service,
        mock_model_service,
        mock_storage_service,
        mock_emotional_tags_data
):
    mock_retrieve_item = AsyncMock()
    mock_retrieve_item.return_value = None
    mock_storage_service.retrieve_item = mock_retrieve_item
    mock_generate_response = Mock()
    mock_generate_response.return_value = mock_emotional_tags_data
    mock_model_service.generate_response = mock_generate_response
    track_id = "1"
    lyrics = "Lyrics for track 1"
    emotion = "joy"

    data = await data_service._get_emotional_tags_data(track_id=track_id, lyrics=lyrics, emotion=emotion)

    assert data == mock_emotional_tags_data
    mock_storage_service.retrieve_item.assert_called_once_with(f"{track_id}_tags_{emotion}")
    mock_model_service.generate_response.assert_called_once_with(f"\nEmotion to Tag: {emotion}\nLyrics: {lyrics}")
    mock_storage_service.store_item.assert_called_once_with(
        key=f"{track_id}_tags_{emotion}",
        value=mock_emotional_tags_data
    )


# 3. Test that get_emotional_tags raises a DataServiceException if a ModelServiceException occurs.
@pytest.mark.asyncio
async def test_get_emotional_tags_storage_failure(data_service, mock_emotional_tags_request):
    mock__get_emotional_tags_data = AsyncMock()
    mock__get_emotional_tags_data.side_effect = StorageServiceException("Test")
    data_service._get_emotional_tags_data = mock__get_emotional_tags_data

    with pytest.raises(
            DataServiceException,
            match=f"Failed to retrieve emotional tags for track_id: 1, lyrics: Lyrics for track 1"
    ):
        await data_service.get_emotional_tags(mock_emotional_tags_request)


# 4. Test that get_emotional_tags raises a DataServiceException if a StorageServiceException occurs.
@pytest.mark.asyncio
async def test_get_emotional_tags_model_failure(data_service, mock_emotional_tags_request):
    mock__get_emotional_tags_data = AsyncMock()
    mock__get_emotional_tags_data.side_effect = ModelServiceException("Test")
    data_service._get_emotional_tags_data = mock__get_emotional_tags_data

    with pytest.raises(
            DataServiceException,
            match=f"Failed to retrieve emotional tags for track_id: 1, lyrics: Lyrics for track 1"
    ):
        await data_service.get_emotional_tags(mock_emotional_tags_request)


# 5. Test that get_emotional_tags raises a DataServiceException if data validation fails.
@pytest.mark.asyncio
async def test_get_emotional_tags_data_validation_failure(data_service, mock_emotional_tags_request):
    mock__get_emotional_tags_data = AsyncMock()
    mock__get_emotional_tags_data.return_value = None
    data_service._get_emotional_tags_data = mock__get_emotional_tags_data

    with pytest.raises(DataServiceException, match="Failed to create EmotionalTagsResponse object"):
        await data_service.get_emotional_tags(mock_emotional_tags_request)


# 6. Test that get_emotional_tags returns expected emotional tags.
@pytest.mark.asyncio
async def test_get_emotional_tags_data_returns_expected_data(
        data_service,
        mock_emotional_tags_request,
        mock_emotional_tags_data
):
    mock__get_emotional_tags_data = AsyncMock()
    mock__get_emotional_tags_data.return_value = mock_emotional_tags_data
    data_service._get_emotional_tags_data = mock__get_emotional_tags_data

    res = await data_service.get_emotional_tags(mock_emotional_tags_request)

    assert res == EmotionalTagsResponse(
        track_id="1",
        lyrics=mock_emotional_tags_data,
        emotion=Emotion.JOY
    )
