import json
from unittest.mock import AsyncMock, Mock

import pytest

from analysis_api.services.data_service import DataService
from analysis_api.services.model_service import ModelService
from analysis_api.services.storage_service import StorageService


@pytest.fixture
def mock_model_service() -> Mock:
    return AsyncMock(spec=ModelService)


@pytest.fixture
def mock_storage_service() -> Mock:
    return AsyncMock(spec=StorageService)


@pytest.fixture
def data_service(mock_model_service, mock_storage_service) -> DataService:
    return DataService(model_service=mock_model_service, storage_service=mock_storage_service)


@pytest.fixture
def mock_emotional_profile_data() -> dict:
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


# -------------------- EMOTIONAL PROFILE -------------------- #
# 1. Test that _get_emotional_profile_data does not call model if data in storage.
# 2. Test that _get_emotional_profile_data calls model if data not in storage.
# 3. Test that get_emotional_profile raises a DataServiceException if a ModelServiceException occurs.
# 4. Test that get_emotional_profile raises a DataServiceException if a StorageServiceException occurs.
# 5. Test that get_emotional_profile raises a DataServiceException if data validation fails.
# 6. Test that get_emotional_profile returns expected emotional profile.
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


@pytest.mark.asyncio
async def test_get_emotional_profile_model_failure(data_service, mock_model_service):
    pass


@pytest.mark.asyncio
async def test_get_emotional_profile_storage_failure(data_service, mock_storage_service):
    pass


@pytest.mark.asyncio
async def test_get_emotional_profile_data_validation_failure(data_service):
    pass


@pytest.mark.asyncio
async def test_get_emotional_profile_data_returns_expected_data(data_service):
    pass

# -------------------- EMOTIONAL TAGS -------------------- #
# 1. Test that _get_emotional_tags_data does not call model if data in storage.
# 2. Test that _get_emotional_tags_data calls model if data not in storage.
# 3. Test that get_emotional_tags raises a DataServiceException if a ModelServiceException occurs.
# 4. Test that get_emotional_tags raises a DataServiceException if a StorageServiceException occurs.
# 5. Test that get_emotional_tags raises a DataServiceException if data validation fails.
# 6. Test that get_emotional_tags returns expected emotional tags.
