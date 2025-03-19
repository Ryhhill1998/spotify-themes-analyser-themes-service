from unittest.mock import Mock, AsyncMock

import pytest
from fastapi.testclient import TestClient

from analysis_api.dependencies import get_data_service
from analysis_api.main import app
from analysis_api.models import Emotion, EmotionalProfileResponse, EmotionalProfile, EmotionalTagsResponse
from analysis_api.services.data_service import DataService, DataServiceException


@pytest.fixture
def mock_data_service() -> Mock:
    return Mock(spec=DataService)


@pytest.fixture
def client(mock_data_service) -> TestClient:
    app.dependency_overrides[get_data_service] = lambda: mock_data_service
    return TestClient(app)


# -------------------- EMOTIONAL PROFILE -------------------- #
# 1. Test /emotional-profile returns a 500 status code if a DataServiceException occurs.
# 2. Test /emotional-profile returns expected response if successful.
@pytest.fixture
def mock_emotional_profile_request() -> dict[str, str]:
    return {"track_id": "1", "lyrics": "Lyrics for track 1"}


@pytest.fixture
def mock_emotional_profile_response() -> EmotionalProfileResponse:
    return EmotionalProfileResponse(
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
            despair=0.05,
            excitement=0.1,
            mystery=0,
            defiance=0.05,
            gratitude=0.1,
            spirituality=0
        )
    )


def test_emotional_profile_data_service_exception(client, mock_data_service, mock_emotional_profile_request):
    mock_get_emotional_profile = AsyncMock()
    mock_get_emotional_profile.side_effect = DataServiceException("Test")
    mock_data_service.get_emotional_profile = mock_get_emotional_profile

    res = client.post(url="/emotions/profile", json=mock_emotional_profile_request)

    assert res.status_code == 500 and res.json() == {"detail": "Something went wrong"}


def test_emotional_profile_data_returns_expected_response(
        client,
        mock_data_service,
        mock_emotional_profile_request,
        mock_emotional_profile_response
):
    mock_get_emotional_profile = AsyncMock()
    mock_get_emotional_profile.return_value = mock_emotional_profile_response
    mock_data_service.get_emotional_profile = mock_get_emotional_profile

    res = client.post(url="/emotions/profile", json=mock_emotional_profile_request)

    assert res.status_code == 200 and res.json() == {
        "track_id": "1",
        "lyrics": "Lyrics for track 1",
        "emotional_profile": {
            "joy": 0.1,
            "sadness": 0.1,
            "anger": 0.2,
            "fear": 0.05,
            "love": 0.1,
            "hope": 0,
            "nostalgia": 0.03,
            "loneliness": 0.02,
            "confidence": 0.1,
            "despair": 0.05,
            "excitement": 0.1,
            "mystery": 0,
            "defiance": 0.05,
            "gratitude": 0.1,
            "spirituality": 0
        }
    }


# -------------------- EMOTIONAL TAGS -------------------- #
# 1. Test /emotional-tags returns a 500 status code if a DataServiceException occurs.
# 2. Test /emotional-tags returns expected response if successful.
@pytest.fixture
def mock_emotional_tags_request() -> dict[str, str]:
    return {
        "track_id": "1",
        "lyrics": "Lyrics for track 1",
        "emotion": "joy"
    }


@pytest.fixture
def mock_emotional_tags_response() -> EmotionalTagsResponse:
    return EmotionalTagsResponse(
        track_id="1",
        lyrics="""<span class="anger">I’ll hurt you</span>""",
        emotion=Emotion.JOY
    )


def test_emotional_tags_data_service_exception(client, mock_data_service, mock_emotional_tags_request):
    mock_get_emotional_tags = AsyncMock()
    mock_get_emotional_tags.side_effect = DataServiceException("Test")
    mock_data_service.get_emotional_tags = mock_get_emotional_tags

    res = client.post(url="/emotions/tags", json=mock_emotional_tags_request)

    assert res.status_code == 500 and res.json() == {"detail": "Something went wrong"}


def test_emotional_tags_data_returns_expected_response(
        client,
        mock_data_service,
        mock_emotional_tags_request,
        mock_emotional_tags_response
):
    mock_get_emotional_tags = AsyncMock()
    mock_get_emotional_tags.return_value = mock_emotional_tags_response
    mock_data_service.get_emotional_tags = mock_get_emotional_tags

    res = client.post(url="/emotions/tags", json=mock_emotional_tags_request)

    assert res.status_code == 200 and res.json() == {
        "track_id": "1",
        "lyrics": """<span class="anger">I’ll hurt you</span>""",
        "emotion": "joy"
    }
