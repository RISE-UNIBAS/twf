"""
Unified AI client for multiple providers including OpenAI, Google Gemini, Anthropic Claude, and Mistral.

This module provides a standardized interface for interacting with various AI models through
their respective APIs. It supports text-based prompts for all providers and multimodal prompts
(text + images) for providers that support them (currently OpenAI and Google Gemini).

The main class, AiApiClient, handles client initialization, prompt construction, and response
processing in a consistent way across all supported providers.
"""
import base64
import time
from datetime import datetime, timezone

import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic
from mistralai import Mistral


class AiApiClient:
    """
    Unified AI API client for multiple model providers.
    
    This class provides a consistent interface for interacting with AI models from
    different providers, including OpenAI (GPT models), Google (Gemini models),
    Anthropic (Claude models), and Mistral. It handles authentication, prompt
    construction, and multimodal content where supported.
    
    Attributes:
        SUPPORTED_APIS (list): List of supported API providers
        api_client: The initialized provider-specific client
        image_resources (list): List of image paths or URLs to include in prompts
        init_time (float): Time when the client was initialized
        end_time (float): Time when the client session ended
    """

    SUPPORTED_APIS = ['openai',
                      'genai',
                      'anthropic',
                      'mistral']

    api_client = None
    image_resources = []

    init_time = None
    end_time = None

    def __init__(self, api, api_key, gpt_role_description=None, temperature=0.5):
        """
        Initialize the AI API client for a specific provider.
        
        Args:
            api (str): The API provider to use ('openai', 'genai', 'anthropic', or 'mistral')
            api_key (str): API key for authentication with the provider
            gpt_role_description (str, optional): System role description for the AI model.
                Defaults to a generic helpful assistant role.
            temperature (float, optional): Controls randomness in the model's responses.
                Higher values (e.g., 0.8) make output more random, lower values (e.g., 0.2)
                make it more deterministic. Defaults to 0.5.
                
        Raises:
            ValueError: If an unsupported API provider is specified
        """
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
        """
        Initialize the appropriate AI client based on the selected API provider.
        
        This method creates the provider-specific client instance using the API key
        supplied in the constructor. For OpenAI, Anthropic, and Mistral, it creates
        a client object. For Google Gemini, it configures the genai library.
        """
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
        """
        Get the elapsed time since client initialization.
        
        If the client has been ended (via end_client), returns the time between
        initialization and ending. Otherwise, returns the time elapsed since
        initialization until now.
        
        Returns:
            float: Elapsed time in seconds
        """
        if self.end_time is None:
            return time.time() - self.init_time
        return self.end_time - self.init_time

    def end_client(self):
        """
        End the client session and record the end time.
        
        This method cleans up the client object and records the time when the
        session ended. This is useful for tracking the total lifetime of a client.
        """
        self.api_client = None
        self.end_time = time.time()

    def add_image_resource(self, resource):
        """
        Add an image resource to be included in the next prompt.
        
        This method supports both local file paths and remote URLs. The appropriate
        handling method will be determined when the prompt is sent.
        
        Args:
            resource (str): Either a local file path or a URL to an image
        """
        self.image_resources.append(resource)

    def clear_image_resources(self):
        """
        Clear all registered image resources.
        
        This method should be called after sending a prompt if you want to
        start fresh with no images for the next prompt.
        """
        self.image_resources = []
        
    def is_url(self, resource):
        """
        Check if a resource is a URL or a local file path.
        
        The method performs a simple string check to determine if the resource
        starts with http:// or https:// protocol identifiers.
        
        Args:
            resource (str): The resource string to check
            
        Returns:
            bool: True if the resource is a URL, False if it's likely a file path
        """
        return resource.startswith(('http://', 'https://'))

    def prompt(self, model, prompt):
        """
        Send a prompt to the AI model and get the response.
        
        This method handles sending the prompt text along with any registered
        image resources to the selected AI model. The specific formatting and
        API calls are handled differently for each provider (OpenAI, Gemini,
        Claude, and Mistral).
        
        For multimodal prompts (text + images):
        - OpenAI and Gemini support both local files and remote image URLs
        - Claude and Mistral currently do not support images
        
        Args:
            model (str): The model identifier to use (e.g., "gpt-4", "gemini-pro")
            prompt (str): The text prompt to send to the model
            
        Returns:
            tuple: A tuple containing (response_object, elapsed_time_in_seconds)
                  The response_object structure varies by provider
        """
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

            for resource in self.image_resources:
                if self.is_url(resource):
                    # For URLs, directly use the URL in the prompt
                    workload_json[0]['content'].append(
                        {"type": "image_url", "image_url": {"url": resource}}
                    )
                else:
                    # For local files, read and encode as base64
                    try:
                        with open(resource, "rb") as image_file:
                            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                        
                        workload_json[0]['content'].append(
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        )
                    except Exception as e:
                        print(f"Error reading image file {resource}: {e}")

            chat_completion = self.api_client.chat.completions.create(
                messages=workload_json,
                model=model,
                temperature=self.temperature
            )
            answer = chat_completion

        if self.api == 'genai':
            model = genai.GenerativeModel(model)
            images = []
            for resource in self.image_resources:
                if self.is_url(resource):
                    # For URLs, fetch the image and provide as blob
                    try:
                        import requests
                        response = requests.get(resource)
                        if response.status_code == 200:
                            # Use the content bytes directly
                            blob = response.content
                            image_parts = genai.upload_blob(blob)
                            images.append(image_parts)
                    except Exception as e:
                        print(f"Error fetching image from URL {resource}: {e}")
                else:
                    # For local files, use the file path
                    try:
                        image_file = genai.upload_file(path=resource)
                        images.append(image_file)
                    except Exception as e:
                        print(f"Error uploading image file {resource}: {e}")

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
        """
        Get a list of available AI models from the current provider.
        
        This method queries the API to get a list of available models that can be used
        with the prompt method. Each provider has its own way of listing models,
        and this method normalizes the results to a consistent format.
        
        Returns:
            list: A list of tuples containing (model_id, created_date) for each available model.
                 The created_date may be None for some providers.
                 
        Raises:
            ValueError: If the API client is not initialized
        """
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