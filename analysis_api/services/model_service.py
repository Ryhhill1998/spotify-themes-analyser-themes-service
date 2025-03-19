import json
from json import JSONDecodeError

from google import genai
from google.genai import types, errors


class ModelServiceException(Exception):
    """Exception raised when generating a response from the model fails."""

    def __init__(self, message: str):
        super().__init__(message)


class ModelService:
    """
    A service for interacting with a generative AI model to generate responses.

    Attributes
    ----------
    SAFETY_SETTINGS : list of types.SafetySetting, class attribute
        Safety settings applied to filter harmful content from model responses.
    client : genai.Client
        The Google GenAI client used for API communication.
    model : str
        The name of the model used for generating responses.
    prompt_template : str
        A template for formatting input prompts.
    response_type : str
        The expected type of the response (e.g., "string", "object").
    response_mime_type : str
        The MIME type of the response (e.g., "application/json").
    temp : float, optional
        The temperature parameter for response variability, by default 0.0.
    top_p : float, optional
        The nucleus sampling parameter controlling response diversity, by default 0.95.
    max_output_tokens : int, optional
        The maximum number of output tokens in the response, by default 1000.
    config : types.GenerateContentConfig
        The configuration settings used when generating responses.

    Methods
    -------
    generate_response(input_data: str) -> dict | str
        Generates a response from the model based on the provided input data.
    """

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
        """
        Parameters
        ----------
        client : genai.Client
            The Google GenAI client used for API communication.
        model : str
            The name of the model used for generating responses.
        prompt_template : str
            A template for formatting input prompts.
        response_type : str
            The expected type of the response (e.g., "string", "object").
        response_mime_type : str
            The MIME type of the response (e.g., "application/json").
        temp : float, optional
            The temperature parameter for response variability, by default 0.0.
        top_p : float, optional
            The nucleus sampling parameter controlling response diversity, by default 0.95.
        max_output_tokens : int, optional
            The maximum number of output tokens in the response, by default 1000.
        """

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
        """
        Generates the configuration settings for content generation.

        Returns
        -------
        types.GenerateContentConfig
            The configuration object containing parameters for text generation.
        """

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
        """
        Formats a user prompt into the content structure required by the model.

        Parameters
        ----------
        prompt : str
            The input prompt to be formatted.

        Returns
        -------
        list of types.Content
            A list containing the formatted prompt content.
        """

        prompt_content = types.Part.from_text(text=prompt)
        contents = [types.Content(role="user", parts=[prompt_content])]

        return contents

    @staticmethod
    def _parse_model_response(response: types.GenerateContentResponse) -> dict | str:
        """
        Parses the model's response and extracts the relevant data.

        Parameters
        ----------
        response : types.GenerateContentResponse
            The raw response received from the model.

        Returns
        -------
        dict or str
            The parsed response content. If the response is in JSON format, a dictionary is returned; otherwise, a
            string.

        Raises
        ------
        ModelServiceException
            If the response cannot be parsed or contains an error.
        """

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
        """
        Generates a response from the model based on the provided input data.

        Parameters
        ----------
        input_data : str
            The text input for which a response is to be generated.

        Returns
        -------
        dict or str
            The model-generated response, either as a dictionary (if JSON) or as a string.

        Raises
        ------
        ModelServiceException
            If an error occurs while communicating with the model API or parsing the response.
        """

        prompt = f"{self.prompt_template}\n{input_data}"
        contents = self._generate_contents(prompt)

        try:
            res = self.client.models.generate_content(model=self.model, contents=contents, config=self.config)
        except errors.APIError as e:
            message = f"Model API error - {e}"
            print(message)
            raise ModelServiceException(message)

        return self._parse_model_response(res)
