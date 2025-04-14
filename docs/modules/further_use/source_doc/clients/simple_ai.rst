Simple AI Clients
=================

The Simple AI Clients module provides unified interfaces to various AI providers, including OpenAI, Google Gemini, Anthropic Claude, and Mistral.
These clients support text-based prompts and (where available) multimodal prompts with images.

Base AI Client
--------------

The base AI client class defines the common interface and functionality that all specific provider implementations inherit from:

.. autoclass:: twf.clients.simple_ai_clients.AiApiClient
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Multimodal Support
------------------

The AI client infrastructure has been extended to support multimodal prompts, combining text and images:

- **Resource Detection**: The `is_url()` method determines if a resource is a URL or file path
- **Image Processing**: Support for both local files and remote URLs
- **Provider Compatibility**: Automatic detection of multimodal support by provider
- **Fallback Mechanism**: Graceful degradation to text-only for providers without image support

Multimodal Methods
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def is_url(self, resource):
        """Check if a resource is a URL or a local file path."""
        return resource.startswith(('http://', 'https://'))
    
    def process_image(self, image_source):
        """Process an image from either a file path or URL."""
        if self.is_url(image_source):
            # Handle URL-based image
            return self.process_image_url(image_source)
        else:
            # Handle file-based image
            return self.process_image_file(image_source)
            
    def prompt_with_images(self, prompt_text, role_description, image_sources):
        """Send a prompt with images to the AI provider."""
        # Implementation depends on the specific provider
        raise NotImplementedError("This method should be implemented by subclasses.")

Provider-Specific Clients
-------------------------

OpenAI Client
~~~~~~~~~~~~~

The OpenAI client class implements multimodal capabilities using the GPT-4 Vision API:

.. code-block:: python

    class OpenAIAiClient(AiApiClient):
        """Client for OpenAI API with multimodal support."""
        
        # Flag indicating that this client supports images
        supports_images = True
        
        def prompt_with_images(self, prompt_text, role_description, image_sources):
            """Send a prompt with images to the OpenAI GPT-4 Vision API."""
            messages = [
                {"role": "system", "content": role_description},
                {"role": "user", "content": []}
            ]
            
            # Add text content if provided
            user_content = messages[1]["content"]
            if prompt_text:
                user_content.append({"type": "text", "text": prompt_text})
            
            # Add image content
            for image_source in image_sources:
                if self.is_url(image_source):
                    # Handle URL-based image
                    user_content.append({
                        "type": "image_url",
                        "image_url": {"url": image_source}
                    })
                else:
                    # Handle file-based image (base64 encoded)
                    with open(image_source, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                        user_content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        })
            
            # Make API call
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1000
            )
            
            return response.choices[0].message.content

Claude Client
~~~~~~~~~~~~~

The Claude client class implements multimodal capabilities for Claude 3 and above:

.. code-block:: python

    class ClaudeAiClient(AiApiClient):
        """Client for Anthropic Claude API with multimodal support."""
        
        # Flag indicating that this client supports images (Claude 3+)
        supports_images = True
        
        def prompt_with_images(self, prompt_text, role_description, image_sources):
            """Send a prompt with images to the Claude API."""
            messages = [
                {
                    "role": "system",
                    "content": role_description
                },
                {
                    "role": "user",
                    "content": []
                }
            ]
            
            # Add text content if provided
            user_content = messages[1]["content"]
            if prompt_text:
                user_content.append({
                    "type": "text",
                    "text": prompt_text
                })
            
            # Add image content
            for image_source in image_sources:
                if self.is_url(image_source):
                    # Handle URL-based image with media_type inference
                    media_type = self.infer_media_type_from_url(image_source)
                    user_content.append({
                        "type": "image",
                        "source": {
                            "type": "url",
                            "url": image_source,
                            "media_type": media_type
                        }
                    })
                else:
                    # Handle file-based image (base64 encoded)
                    with open(image_source, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                        media_type = self.infer_media_type_from_path(image_source)
                        user_content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image
                            }
                        })
            
            # Make API call
            response = anthropic.Anthropic(api_key=self.api_key).messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=messages
            )
            
            return response.content[0].text

Gemini Client
~~~~~~~~~~~~~

The Gemini client class implements native multimodal capabilities:

.. code-block:: python

    class GeminiAiClient(AiApiClient):
        """Client for Google Gemini API with native multimodal support."""
        
        # Flag indicating that this client supports images
        supports_images = True
        
        def prompt_with_images(self, prompt_text, role_description, image_sources):
            """Send a prompt with images to the Gemini API."""
            from google.generativeai import GenerationConfig
            import PIL.Image
            
            # Initialize contents list with system prompt
            contents = [{"role": "system", "parts": [{"text": role_description}]}]
            
            # User message with text and images
            user_parts = []
            if prompt_text:
                user_parts.append({"text": prompt_text})
            
            # Add image content
            for image_source in image_sources:
                if self.is_url(image_source):
                    # For URL-based images, download temporarily
                    import requests
                    from io import BytesIO
                    
                    response = requests.get(image_source)
                    image = PIL.Image.open(BytesIO(response.content))
                    user_parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image}})
                else:
                    # For file-based images
                    image = PIL.Image.open(image_source)
                    user_parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image}})
            
            # Add user message with all parts
            contents.append({"role": "user", "parts": user_parts})
            
            # Make API call
            config = GenerationConfig(
                temperature=0.1,
                top_p=1,
                top_k=32,
                max_output_tokens=2048,
            )
            
            response = self.model.generate_content(
                contents,
                generation_config=config
            )
            
            return response.text

Mistral Client
~~~~~~~~~~~~~~

The Mistral client class implements basic multimodal support:

.. code-block:: python

    class MistralAiClient(AiApiClient):
        """Client for Mistral AI API with basic multimodal support."""
        
        # Flag indicating whether this client supports images (depends on model)
        supports_images = False  # Set to True for models that support images
        
        def __init__(self, api_key, model=None):
            """Initialize with potential image support check based on model."""
            super().__init__(api_key, model)
            
            # Check if the selected model supports images
            self.supports_images = model in ["mistral-large-latest", "mistral-medium-latest"]
            
        def prompt_with_images(self, prompt_text, role_description, image_sources):
            """Send a prompt with images to the Mistral API for supported models."""
            if not self.supports_images:
                # Fall back to text-only for unsupported models
                return self.prompt(prompt_text, role_description)
                
            # Implementation for models that support images
            # ...

Image Processing Example
------------------------

Example of multimodal processing with the OpenAI client:

.. code-block:: python

    # Example of using the OpenAI client with both text and images
    client = OpenAIAiClient(api_key="your_api_key")
    
    # Text prompt
    text_result = client.prompt("Describe this document", "You are a helpful assistant")
    
    # Multimodal prompt with both text and images
    image_sources = [
        "https://example.com/image1.jpg",
        "/path/to/local/image2.jpg"
    ]
    multimodal_result = client.prompt_with_images(
        "What can you see in these images?",
        "You are a helpful assistant",
        image_sources
    )

Module Contents
---------------

.. automodule:: twf.clients.simple_ai_clients
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :exclude-members: SUPPORTED_APIS