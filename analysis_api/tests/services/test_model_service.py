from unittest.mock import Mock

import pytest

from analysis_api.services.model_service import ModelService


# 1. Test that _parse_model_response raises ModelServiceException if response.text not valid JSON.
# 2. Test that _parse_model_response raises ModelServiceException if 'error' in json_response.
# 3. Test that _parse_model_response raises ModelServiceException if 'response' not in json_response.
# 4. Test that _parse_model_response returns expected string.
# 5. Test that _parse_model_response returns expected JSON.
# 6. Test that generate_response raises ModelServiceException if Model API errors occurs.


@pytest.fixture
def model_service() -> ModelService:
    return ModelService(
        project_id="",
        location="",
        model="",
        prompt_template="",
        temp=0.0,
        top_p=0.0,
        max_output_tokens=0
    )



