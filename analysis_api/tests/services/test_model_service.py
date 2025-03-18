from unittest import mock
from unittest.mock import Mock, MagicMock

import pytest
from google import genai
from google.genai import types

from analysis_api.services.model_service import ModelService, ModelServiceException


# 1. Test that generate_response raises ModelServiceException if response.text not valid JSON.
# 2. Test that generate_response raises ModelServiceException if 'error' in json_response.
# 3. Test that generate_response raises ModelServiceException if 'response' not in json_response.
# 4. Test that generate_response returns expected string.
# 5. Test that generate_response returns expected JSON.
# 6. Test that generate_response raises ModelServiceException if Model API errors occurs.


@pytest.fixture
def mock_client() -> Mock:
    return Mock(spec=genai.Client)


@pytest.fixture
def model_service(mock_client) -> ModelService:
    return ModelService(
        client=mock_client,
        model="",
        prompt_template="",
        response_type="",
        response_mime_type="",
        temp=0.0,
        top_p=0.0,
        max_output_tokens=0
    )


def test_generate_response_invalid_json(model_service):
    mock__generate_contents = Mock()
    mock__generate_contents.return_value = "prompt"
    mock_generate_content = Mock()
    mock_response = Mock(spec=types.GenerateContentResponse)
    mock_response.text = "invalid JSON"
    mock_generate_content.return_value = mock_response

    model_service._generate_contents = mock__generate_contents
    model_service.client.models.generate_content = mock_generate_content

    with pytest.raises(ModelServiceException, match="res.text is not valid JSON"):
        model_service.generate_response("")


def test_generate_response_error_key_in_json(model_service):
    mock__generate_contents = Mock()
    mock__generate_contents.return_value = "prompt"
    mock_generate_content = Mock()
    mock_response = Mock(spec=types.GenerateContentResponse)
    mock_response.text = '{"error": {"message": "Test error"}, "response": "Test response"}'
    mock_generate_content.return_value = mock_response

    model_service._generate_contents = mock__generate_contents
    model_service.client.models.generate_content = mock_generate_content

    with pytest.raises(ModelServiceException, match="Model error"):
        model_service.generate_response("")
