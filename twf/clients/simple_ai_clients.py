"""Simple AI API client for OpenAI, GenAI, and Anthropic."""
import base64
import time
from datetime import datetime, timezone

import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic
from mistralai import Mistral


class AiApiClient:
    """Simple AI API client for OpenAI, GenAI, and Anthropic."""

    SUPPORTED_APIS = ['openai',
                      'genai',
                      'anthropic',
                      'mistral']

    api_client = None
    image_resources = []

    init_time = None
    end_time = None

    def __init__(self, api, api_key, gpt_role_description=None, temperature=0.5):
        if api not in self.SUPPORTED_APIS:
            raise ValueError('Unsupported API')

        self.init_time = time.time()
        self.api = api
        self.api_key = api_key
        self.gpt_role_description = gpt_role_description
        if self.gpt_role_description is None:
            self.gpt_role_description = "A useful assistant that can help you with a variety of tasks."
        self.temperature = temperature

        self.init_client()

    def init_client(self):
        """Initialize the AI client."""
        if self.api == 'openai':
            self.api_client = OpenAI(
                api_key=self.api_key,
            )

        if self.api == 'genai':
            genai.configure(api_key=self.api_key)

        if self.api == 'anthropic':
            self.api_client = Anthropic(
                api_key=self.api_key,
            )

        if self.api == 'mistral':
            self.api_client = Mistral(
                api_key=self.api_key
            )

    @property
    def elapsed_time(self):
        """Return the elapsed time since the client was initialized."""
        if self.end_time is None:
            return time.time() - self.init_time
        return self.end_time - self.init_time

    def end_client(self):
        """End the client session."""
        self.api_client = None
        self.end_time = time.time()

    def add_image_resource(self, path):
        """Add an image resource to the client"""
        self.image_resources.append(path)

    def clear_image_resources(self):
        """Clear the image resources"""
        self.image_resources = []

    def prompt(self, model, prompt):
        """Prompt the AI model with a given prompt."""
        prompt_start = time.time()
        answer = None

        if self.api == 'openai':
            workload_json = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ]
                },
                {
                    "role": "system",
                    "content": self.gpt_role_description
                }
            ]

            for img_path in self.image_resources:
                with open(img_path, "rb") as image_file:
                    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

                workload_json[0]['content'].append(
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                )

            chat_completion = self.api_client.chat.completions.create(
                messages=workload_json,
                model=model,
                temperature=self.temperature
            )
            answer = chat_completion

        if self.api == 'genai':
            model = genai.GenerativeModel(model)
            images = []
            for img_path in self.image_resources:
                image_file = genai.upload_file(path=img_path)
                images.append(image_file)

            response = model.generate_content([prompt] + images)
            answer = response

        if self.api == 'anthropic':
            message = self.api_client.messages.create(
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model,
            )
            answer = message

        if self.api == 'mistral':
            workload = [
                {
                    "content": prompt,
                    "role": "user",
                }
            ]

            message = self.api_client.chat.complete(
                model=model,
                messages=workload
            )
            answer = message

        end_time = time.time()
        elapsed_time = end_time - prompt_start
        return answer, elapsed_time

    def get_model_list(self):
        """Get the list of available models."""
        if not self.api == "genai" and self.api_client is None:
            raise ValueError('API client is not initialized.')

        model_list = []
        if self.api == 'openai':
            raw_list = self.api_client.models.list()
            for model in raw_list:
                readable_date = datetime.fromtimestamp(model.created, tz=timezone.utc).strftime('%Y-%m-%d')
                model_list.append((model.id, readable_date))

        if self.api == 'genai':
            raw_list = genai.list_models()
            for model in raw_list:
                if model.display_name.startswith("Gemini"):
                    model_list.append((model.name.lstrip("models/"), None))

        if self.api == 'anthropic':
            raw_list = self.api_client.models.list()
            for model in raw_list:
                readable_date = datetime.date(model.created_at).strftime('%Y-%m-%d')
                model_list.append((model.id, readable_date))

        if self.api == 'mistral':
            raw_list = self.api_client.models.list()
            for model in raw_list.data:
                completion = model.capabilities.completion_chat
                if completion:
                    readable_date = datetime.fromtimestamp(model.created, tz=timezone.utc).strftime('%Y-%m-%d')
                    model_list.append((model.id, readable_date))

        return model_list