Simple AI Clients
===============

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
-----------------

The AI client infrastructure has been extended to support multimodal prompts, combining text and images:

- **Resource Detection**: The `is_url()` method determines if a resource is a URL or file path
- **Image Processing**: Support for both local files and remote URLs
- **Provider Compatibility**: Automatic detection of multimodal support by provider
- **Fallback Mechanism**: Graceful degradation to text-only for providers without image support

Multimodal Methods
~~~~~~~~~~~~~~~~~

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
------------------------

OpenAI Client
~~~~~~~~~~~~~

.. autoclass:: twf.clients.simple_ai_clients.OpenAIAiClient
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Claude Client
~~~~~~~~~~~~

.. autoclass:: twf.clients.simple_ai_clients.ClaudeAiClient
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Gemini Client
~~~~~~~~~~~~

.. autoclass:: twf.clients.simple_ai_clients.GeminiAiClient
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Mistral Client
~~~~~~~~~~~~~

.. autoclass:: twf.clients.simple_ai_clients.MistralAiClient
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Image Processing Example
----------------------

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
-------------

.. automodule:: twf.clients.simple_ai_clients
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__
   :exclude-members: SUPPORTED_APIS