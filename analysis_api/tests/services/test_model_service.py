import json
from unittest.mock import Mock

import pytest
import requests
from google import genai
from google.genai import types, errors

from analysis_api.services.model_service import ModelService, ModelServiceException


# 1. Test that generate_response raises ModelServiceException if response.text not valid JSON.
# 2. Test that generate_response raises ModelServiceException if 'error' in json_response.
# 3. Test that generate_response raises ModelServiceException if 'response' not in json_response.
# 4. Test that generate_response raises ModelServiceException if Model API errors occurs.
# 5. Test that generate_response returns expected string.
# 6. Test that generate_response returns expected JSON.


@pytest.fixture
def mock_client() -> Mock:
    return Mock(spec=genai.Client)


@pytest.fixture
def mock__generate_contents() -> Mock:
    mock = Mock()
    mock.return_value = "prompt"
    return mock


@pytest.fixture
def mock_generate_content() -> Mock:
    mock = Mock(spec=types.GenerateContentResponse)
    mock_response = Mock()
    mock_response.text = ""
    mock.return_value = mock_response
    return mock


@pytest.fixture
def model_service(mock_client, mock__generate_contents, mock_generate_content) -> ModelService:
    ms = ModelService(
        client=mock_client,
        model="",
        prompt_template="",
        response_type="",
        response_mime_type="",
        temp=0.0,
        top_p=0.0,
        max_output_tokens=0
    )
    ms._generate_contents = mock__generate_contents
    ms.client.models.generate_content = mock_generate_content
    return ms


def test_generate_response_invalid_json(model_service, mock_generate_content):
    mock_generate_content.return_value.text = "invalid JSON"

    with pytest.raises(ModelServiceException, match="res.text is not valid JSON"):
        model_service.generate_response("")


def test_generate_response_error_key_in_json(model_service, mock_generate_content):
    mock_generate_content.return_value.text = '{"error": {"message": "Test error"}, "response": "Test response"}'

    with pytest.raises(ModelServiceException, match="Model error"):
        model_service.generate_response("")


def test_generate_response_no_response_key_in_json(model_service, mock_generate_content):
    mock_generate_content.return_value.text = '{"data": "Test data"}'

    with pytest.raises(ModelServiceException, match="json_response has no key 'response'"):
        model_service.generate_response("")


def test_generate_response_api_error(model_service, mock_generate_content):
    mock_response = Mock(spec=requests.Response)
    mock_generate_content.side_effect = errors.APIError(code=500, response=mock_response)

    with pytest.raises(ModelServiceException, match="Model API error"):
        model_service.generate_response("")


@pytest.mark.parametrize("expected_response", ["string", {"key": "value"}])
def test_generate_response_returns_expected_response(model_service, mock_generate_content, expected_response):
    mock_generate_content.return_value.text = json.dumps({"response": expected_response})

    assert model_service.generate_response("") == expected_response
