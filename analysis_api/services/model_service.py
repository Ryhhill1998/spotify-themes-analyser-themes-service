import json

from google import genai
from google.genai import types


class ModelService:
    def __init__(
            self,
            project_id: str,
            location: str,
            model: str,
            prompt_template: str,
            temp: float = 0.0,
            top_p: float = 0.95,
            max_output_tokens: int = 1000
    ):
        self.client = genai.Client(vertexai=True, project=project_id, location=location)
        self.model = model
        self.prompt_template = prompt_template
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
            safety_settings=[types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="OFF"
            ), types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="OFF"
            ), types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="OFF"
            ), types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="OFF"
            )],
            response_mime_type="application/json",
            response_schema={"type": "OBJECT", "properties": {"response": {"type": "STRING"}}},
        )

    @staticmethod
    def _generate_contents(prompt: str) -> list[types.Content]:
        return [types.Content(role="user", parts=[prompt])]

    def generate_response(self, data: str):
        prompt = f"{self.prompt_template}\n{data}"

        res = self.client.models.generate_content(
            model=self.model,
            contents=self._generate_contents(prompt),
            config=self.config
        )

        data = json.loads(json.loads(res.text)["response"])

        return data
