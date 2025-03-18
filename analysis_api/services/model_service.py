import json
from json import JSONDecodeError

from google import genai
from google.genai import types, errors


class ModelServiceException(Exception):
    """Exception raised when generating a response from the model fails."""

    def __init__(self, message: str):
        super().__init__(message)


class ModelService:
    SAFETY_SETTINGS = [
        types.SafetySetting(category=types.HarmCategory(c), threshold=types.HarmBlockThreshold("OFF"))
        for c in [
            "HARM_CATEGORY_HATE_SPEECH",
            "HARM_CATEGORY_DANGEROUS_CONTENT",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "HARM_CATEGORY_HARASSMENT"
        ]
    ]

    def __init__(
            self,
            client: genai.Client,
            model: str,
            prompt_template: str,
            response_type: str,
            response_mime_type: str,
            temp: float = 0.0,
            top_p: float = 0.95,
            max_output_tokens: int = 1000
    ):
        self.client = client
        self.model = model
        self.prompt_template = prompt_template
        self.response_type = response_type
        self.response_mime_type = response_mime_type
        self.temp = temp
        self.top_p = top_p
        self.max_output_tokens = max_output_tokens
        self.config = self._generate_content_config()

    def _generate_content_config(self) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            temperature=self.temp,
            top_p=self.top_p,
            max_output_tokens=self.max_output_tokens,
            response_modalities=["TEXT"],
            safety_settings=self.SAFETY_SETTINGS,
            response_mime_type=self.response_mime_type,
            response_schema={"type": "OBJECT", "properties": {"response": {"type": self.response_type}}},
        )

    @staticmethod
    def _generate_contents(prompt: str) -> list[types.Content]:
        prompt_content = types.Part.from_text(text=prompt)
        contents = [types.Content(role="user", parts=[prompt_content])]

        return contents

    @staticmethod
    def _parse_model_response(response: types.GenerateContentResponse) -> dict | str:
        try:
            json_response = json.loads(response.text)
        except JSONDecodeError as e:
            message = f"res.text is not valid JSON: {response.text} - {e}"
            print(message)
            raise ModelServiceException(message)

        if "error" in json_response:
            raise ModelServiceException(f"Model error: {json_response['error'].get('message', 'Unknown error')}")

        response_data = json_response.get("response")

        if response_data is None:
            message = f"json_response has no key 'response': {json_response}"
            print(message)
            raise ModelServiceException(message)

        return response_data

    def generate_response(self, input_data: str) -> dict | str:
        prompt = f"{self.prompt_template}\n{input_data}"
        contents = self._generate_contents(prompt)

        try:
            res = self.client.models.generate_content(model=self.model, contents=contents, config=self.config)
        except errors.APIError as e:
            message = f"Model API error - {e}"
            print(message)
            raise ModelServiceException(message)

        return self._parse_model_response(res)
