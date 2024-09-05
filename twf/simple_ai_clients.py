import base64
import json
import time

import google.generativeai as genai
import requests
from openai import OpenAI


class AiApiClient:
    """Simple AI API client for OpenAI, GenAI, and Anthropic."""

    SUPPORTED_APIS = ['openai',
                      'genai',
                      'anthropic']

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
        if self.api == 'openai':
            self.api_client = OpenAI(
                api_key=self.api_key,
            )

        if self.api == 'genai':
            genai.configure(api_key=self.api_key)

        if self.api == 'anthropic':
            # No client to initialize
            pass

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
            message = response.text
            answer = message

        if self.api == 'anthropic':
            headers = {
                'x-api-key': f'{self.api_key}',
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json',
            }
            data = {
                "model": model,
                "max_tokens_to_sample": 1024,
                "prompt": f"\n\nHuman: {prompt}\nAssistant:"
            }
            api_url = 'https://api.anthropic.com/v1/complete'
            response = requests.post(api_url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                answer = response.json()
            else:
                answer = f"Error: {response.status_code}: {response.text}"

        end_time = time.time()
        elapsed_time = end_time - prompt_start
        return answer, elapsed_time
