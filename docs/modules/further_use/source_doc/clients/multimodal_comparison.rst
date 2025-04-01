Multimodal Provider Comparison
==========================

This page compares the implementation differences between the various AI providers when handling multimodal content (text + images).

Provider Capabilities
--------------------

Each AI provider has different capabilities and requirements for handling multimodal inputs:

+---------------+----------------+--------------------+---------------------------+
| Provider      | Image Support  | Image Format       | Special Considerations    |
+===============+================+====================+===========================+
| OpenAI        | GPT-4 Vision   | URL, Base64        | Limited to 20MB/request   |
+---------------+----------------+--------------------+---------------------------+
| Claude        | Claude 3+      | URL, Base64        | Requires media_type       |
+---------------+----------------+--------------------+---------------------------+
| Gemini        | All models     | PIL Image objects  | Native multimodal support |
+---------------+----------------+--------------------+---------------------------+
| Mistral       | Large models   | URL, Base64        | Limited format options    |
+---------------+----------------+--------------------+---------------------------+

Implementation Comparison
------------------------

Below is a detailed comparison of the different implementations for each provider:

OpenAI Implementation
~~~~~~~~~~~~~~~~~~~~

OpenAI uses a content array with different types for text and images:

.. code-block:: python

    class OpenAIMultiModalClient(AiApiClient):
        """Client for OpenAI API with multimodal support."""
        
        supports_images = True
        
        def prompt_with_images(self, prompt_text, role_description, image_sources):
            """Send a prompt with text and images to the OpenAI API."""
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
                    # Direct URL reference
                    user_content.append({
                        "type": "image_url",
                        "image_url": {"url": image_source}
                    })
                else:
                    # Base64 encoded image
                    with open(image_source, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                        user_content.append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        })
            
            # Make API call with vision model
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=1000
            )
            
            return response.choices[0].message.content

Claude Implementation
~~~~~~~~~~~~~~~~~~~~

Claude uses a similar content array approach but with different structure:

.. code-block:: python

    class ClaudeMultiModalClient(AiApiClient):
        """Client for Anthropic Claude API with multimodal support."""
        
        supports_images = True
        
        def prompt_with_images(self, prompt_text, role_description, image_sources):
            """Send a prompt with text and images to the Claude API."""
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
                    # URL-based image with media_type inference
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
                    # File-based image with base64 encoding
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
            
            # Make API call with Claude 3
            response = anthropic.Anthropic(api_key=self.api_key).messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=messages
            )
            
            return response.content[0].text
        
        def infer_media_type_from_url(self, url):
            """Infer the media type from a URL."""
            # Extract extension from URL
            extension = url.split('.')[-1].lower()
            return self._get_media_type_from_extension(extension)
            
        def infer_media_type_from_path(self, path):
            """Infer the media type from a file path."""
            # Extract extension from file path
            extension = os.path.splitext(path)[1][1:].lower()
            return self._get_media_type_from_extension(extension)
            
        def _get_media_type_from_extension(self, extension):
            """Convert file extension to media type."""
            media_types = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp',
                'tiff': 'image/tiff'
            }
            return media_types.get(extension, 'image/jpeg')  # Default to JPEG

Gemini Implementation
~~~~~~~~~~~~~~~~~~~~

Gemini uses a different approach with PIL Image objects:

.. code-block:: python

    class GeminiMultiModalClient(AiApiClient):
        """Client for Google Gemini API with native multimodal support."""
        
        supports_images = True
        
        def prompt_with_images(self, prompt_text, role_description, image_sources):
            """Send a prompt with text and images to the Gemini API."""
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

Mistral Implementation
~~~~~~~~~~~~~~~~~~~~~

Mistral has more limited multimodal support:

.. code-block:: python

    class MistralMultiModalClient(AiApiClient):
        """Client for Mistral AI API with basic multimodal support."""
        
        # Default to False, will be determined by model
        supports_images = False
        
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
                
            # Initialize messages list
            messages = [
                {"role": "system", "content": role_description},
                {"role": "user", "content": []}
            ]
            
            # Add text content if provided
            user_content = messages[1]["content"]
            if prompt_text:
                user_content.append({"type": "text", "text": prompt_text})
            
            # Add image content (limited to 2 images for performance)
            for image_source in image_sources[:2]:
                if self.is_url(image_source):
                    # URL-based image
                    user_content.append({
                        "type": "image", 
                        "image": {"url": image_source}
                    })
                else:
                    # File-based image with base64 encoding
                    with open(image_source, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                        user_content.append({
                            "type": "image",
                            "image": {"data": base64_image}
                        })
            
            # Make API call
            response = self.client.chat(
                model=self.model,
                messages=messages
            )
            
            return response.choices[0].message.content

Best Practices
-------------

When implementing multimodal functionality across multiple providers, consider these best practices:

1. **Check Support First**: Always check if the provider/model supports multimodal inputs before attempting to use them
2. **Fallback Gracefully**: Provide fallback to text-only mode when multimodal is not supported
3. **Handle Multiple Formats**: Support both URL and file-based images
4. **Optimize Image Size**: Scale images appropriately based on provider limits
5. **Error Handling**: Implement robust error handling for image processing
6. **Standardize Interface**: Use a consistent interface across providers for easier integration

Implementation Challenges
------------------------

Common challenges when implementing multimodal support:

1. **Different API Formats**: Each provider requires different formats for including images
2. **Size Limitations**: Providers have different limits on image size and count
3. **Performance Issues**: Including too many images can lead to performance degradation
4. **Content Type Detection**: Correctly detecting image content types can be challenging
5. **Token Usage**: Multimodal requests typically use more tokens and thus cost more
6. **Quality vs. Size**: Balancing image quality with size limitations