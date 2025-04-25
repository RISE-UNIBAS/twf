"""
Unified AI client for multiple providers including OpenAI, Google Gemini, Anthropic Claude, and Mistral.

This module provides a standardized interface for interacting with various AI models through
their respective APIs. It supports text-based prompts for all providers and multimodal prompts
(text + images) for providers that support them (currently OpenAI and Google Gemini).

The main class, AiApiClient, handles client initialization, prompt construction, and response
processing in a consistent way across all supported providers. For multimodal content,
it provides methods to add image resources (either local files or remote URLs), build
appropriate prompts for each provider, and clean up resources after use.

Key features:
- Unified interface for all supported AI providers
- Support for both text-only and multimodal (text + images) content
- Flexible handling of both local image files and remote image URLs
- Consistent response format and timing information
- Provider-specific optimizations for each API

Technical implementation details:
- OpenAI: Uses the chat completions API with multimodal support
- Google Gemini: Uses the GenerativeModel class with image uploads
- Anthropic Claude: Uses the messages API (text-only currently)
- Mistral: Uses the chat completion API (text-only currently)

For multimodal support, see the add_image_resource() and clear_image_resources() methods.
"""
import base64
import tempfile
import time
from datetime import datetime, timezone

import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic
from mistralai import Mistral


class AiApiClient:
    """
    Unified AI API client for multiple model providers with multimodal support.
    
    This class provides a consistent interface for interacting with AI models from
    different providers, including OpenAI (GPT models), Google (Gemini models),
    Anthropic (Claude models), and Mistral. It handles authentication, prompt
    construction, and multimodal content where supported.
    
    The client abstracts away the differences between various AI APIs, providing
    a consistent interface for both text-only and multimodal (text + images) prompts.
    For providers that support multimodal content (currently OpenAI and Google Gemini),
    it handles the specific requirements for image formatting and submission.
    
    Attributes:
        SUPPORTED_APIS (list): List of supported API providers
        api_client: The initialized provider-specific client
        image_resources (list): List of image paths or URLs to include in prompts
        init_time (float): Time when the client was initialized
        end_time (float): Time when the client session ended
        api (str): The selected API provider ('openai', 'genai', 'anthropic', 'mistral')
        api_key (str): The API key used for authentication
        gpt_role_description (str): System role description for the AI
        temperature (float): Controls randomness in model responses (0.0-1.0)
    
    Multimodal Support:
        - OpenAI: Full support for images via GPT-4 Vision API
        - Google Gemini: Full support for images via Gemini Pro Vision
        - Claude: Text-only currently, multimodal support pending
        - Mistral: Text-only currently, multimodal support pending
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
        
        Creates a unified client interface for interacting with various AI providers.
        The client provides consistent methods for both text-only and multimodal
        interactions, with provider-specific optimizations handled internally.
        
        Args:
            api (str): The API provider to use ('openai', 'genai', 'anthropic', or 'mistral')
            api_key (str): API key for authentication with the provider
            gpt_role_description (str, optional): System role description for the AI model.\
                Defaults to a generic helpful assistant role.
            temperature (float, optional): Controls randomness in the model's responses. \
                Higher values (e.g., 0.8) make output more random, lower values (e.g., 0.2) \
                make it more deterministic. Defaults to 0.5.
                
        Raises:
            ValueError: If an unsupported API provider is specified
            
        Multimodal Support Details:
            After initialization, the client can process multimodal content via:
            1. add_image_resource() - Register images to include in the next prompt
            2. prompt() - Send the prompt with any registered images
            3. clear_image_resources() - Clean up after processing
            
            Multimodal support varies by provider:
            - OpenAI: Supported in GPT-4 Vision and later GPT-4 models
            - Google Gemini: Supported in Gemini Pro Vision and Gemini 1.5
            - Claude & Mistral: Not currently supported (text-only)
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
        supplied in the constructor. Each provider has its own client initialization
        approach:
        
        - OpenAI: Creates an OpenAI client object with the API key
        - Google Gemini: Configures the genai library with the API key
        - Anthropic: Creates an Anthropic client object with the API key
        - Mistral: Creates a Mistral client object with the API key
        
        All these clients support basic text prompts. For multimodal support:
        - OpenAI supports images through the chat completions API
        - Google Gemini supports images through the GenerativeModel API
        - Anthropic and Mistral clients are initialized but don't yet support \
          multimodal content in this implementation
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
        
        This is useful for tracking overall client resource usage and performance,
        especially for multimodal requests which tend to be more resource-intensive
        and time-consuming than text-only requests.
        
        Returns:
            float: Elapsed time in seconds
            
        Note:
            This measures the total client lifetime, not individual request time.
            For request-specific timing, see the second return value from prompt().
        """
        if self.end_time is None:
            return time.time() - self.init_time
        return self.end_time - self.init_time

    def end_client(self):
        """
        End the client session and record the end time.
        
        This method cleans up the client object and records the time when the
        session ended. This is useful for tracking the total lifetime of a client,
        which helps monitor resource usage and performance, especially for 
        multimodal requests which may consume more resources.
        
        The client is considered inactive after this method is called. To use
        the client again, you would need to create a new instance.
        
        Note:
            - This does not automatically clear image resources
            - If you end a client that has registered images, you should call
              clear_image_resources() first to ensure proper cleanup
        """
        self.api_client = None
        self.end_time = time.time()

    def add_image_resource(self, resource):
        """
        Add an image resource to be included in the next prompt.
        
        This method supports both local file paths and remote URLs. The appropriate
        handling method will be determined when the prompt is sent. Each provider
        has its own implementation for handling images:
        
        - OpenAI: Uses image_url content type with base64 encoding for local files
          or direct URL references for remote images
        - Google Gemini: Uses genai.upload_file for local files and fetches content
          for remote URLs with genai.upload_blob
        - Claude & Mistral: Currently don't support images, so these are ignored
        
        Images are stored in the client's image_resources list and processed when
        the prompt() method is called.
        
        Args:
            resource (str): Either a local file path or a URL to an image
            
        Notes:
            - For best results with OpenAI, use JPEG or PNG images
            - For Google Gemini, most common image formats are supported
            - URLs should begin with http:// or https:// to be recognized as remote
            - The image itself is not loaded until the prompt is sent, minimizing memory usage
        """
        self.image_resources.append(resource)

    def clear_image_resources(self):
        """
        Clear all registered image resources.
        
        This method should be called after sending a prompt if you want to
        start fresh with no images for the next prompt. It's important to call
        this method after processing multimodal requests to avoid unintentionally
        including images in subsequent requests and to free up any resources.
        
        For provider-specific details:
        - OpenAI: Images are processed and encoded during the prompt call, \
          so clearing them frees memory and prevents reuse
        - Google Gemini: Images might remain in memory on the Gemini service side, \
          but clearing locally prevents them from being re-uploaded
        
        The BaseTWFTask.process_single_ai_request method automatically calls
        this method after processing a multimodal request.
        """
        self.image_resources = []
        
    def is_url(self, resource):
        """
        Check if a resource is a URL or a local file path.
        
        The method performs a simple string check to determine if the resource
        starts with http:// or https:// protocol identifiers. This is used to
        determine the appropriate handling method for image resources in
        multimodal prompts.
        
        For multimodal prompts, resource handling differs based on type:
        - URLs: Typically processed by making a request to fetch the content or \
          by passing the URL directly to the AI provider
        - File paths: Read from the local filesystem and processed according to \
          each provider's requirements (e.g., base64 encoding for OpenAI)
        
        
        Args:
            resource (str): The resource string to check
            
        
        Returns:
            bool: True if the resource is a URL, False if it's likely a file path
        """
        return resource.startswith(('http://', 'https://'))

    def has_multimodal_support(self):
        """
        Check if the current API provider supports multimodal content.

        This method checks the selected API provider and returns True if
        it supports multimodal content (text + images) in the prompt method.

        Currently, only OpenAI and Google Gemini support multimodal prompts.
        Anthropic Claude and Mistral do not support images in this implementation.

        Returns:
            bool: True if the provider supports multimodal content, False otherwise
        """
        return self.api in ['openai', 'genai']

    def prompt(self, model, prompt):
        """
        Send a prompt to the AI model and get the response.
        
        This method handles sending the prompt text along with any registered
        image resources to the selected AI model. The specific formatting and
        API calls are handled differently for each provider (OpenAI, Gemini,
        Claude, and Mistral).
        
        For multimodal prompts (text + images):
        - OpenAI: Uses the Chat Completions API with multimodal content support

          * Images are sent as image_url content items in the message
          * Local files are base64 encoded with data URI scheme
          * Remote URLs are sent directly in the image_url object
          * Supported in models like gpt-4-vision and later gpt-4 models
        
        - Google Gemini: Uses the GenerativeModel API with multimodal support

          * Images are uploaded via genai.upload_file or genai.upload_blob
          * Both local files and remote URLs are supported
          * Supported in models like gemini-pro-vision and gemini-1.5-pro
        
        - Claude and Mistral: Currently do not support images in API

          * Any registered images will be ignored
          * Only the text prompt will be processed
        
        Args:
            model (str): The model identifier to use (e.g., "gpt-4", "gemini-pro")
            prompt (str): The text prompt to send to the model
            
        Returns:
            tuple: A tuple containing (response_object, elapsed_time_in_seconds) \
                  The response_object structure varies by provider
                  
        Usage Notes:
        - To use multimodal prompts, first call add_image_resource() for each image
        - After receiving the response, call clear_image_resources() to clean up
        - The temperature setting from initialization is used for all providers
        - Response times can vary significantly with multimodal content
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
                            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=True) as tmp:
                                tmp.write(response.content)
                                tmp.flush()  # Ensure everything is written before upload
                                image_part = genai.upload_file(path=tmp.name)
                                images.append(image_part)
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
        
        For multimodal support, you should generally select models with vision capabilities:
        - OpenAI: Models like 'gpt-4-vision-preview' or recent 'gpt-4' versions
        - Google Gemini: Models with 'vision' in the name or Gemini 1.5 models
        - Anthropic: Currently no multimodal models supported in this implementation
        - Mistral: Currently no multimodal models supported in this implementation
        
        The return format is standardized across all providers to make model selection
        easier in the TWF interface.
        
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