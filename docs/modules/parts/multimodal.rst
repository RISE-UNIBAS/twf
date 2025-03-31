Multimodal AI Features
====================

Overview
--------

The TWF application supports multimodal AI functionality, allowing users to combine text and images in their prompts when querying AI providers. This feature enhances the capabilities of the platform by enabling users to process both textual and visual information together.

Supported Providers
------------------

The following AI providers support multimodal functionality:

* **OpenAI**: GPT-4 Vision API supports text and images
* **Google Gemini**: Native support for multimodal inputs
* **Anthropic Claude**: Version 3 and above support multimodal prompts
* **Mistral**: Limited multimodal support (check current capabilities)

Prompt Modes
-----------

The multimodal feature supports three different prompt modes:

1. **Text Only**: Only text content is sent to the AI provider
2. **Images Only**: Only image content is sent without text (except required system prompts)
3. **Text + Images**: Both text and images are sent together

Image Selection
--------------

When using a mode that includes images:

* The system automatically selects up to 5 images per document
* Images are selected based on page number order
* Images are directly accessed via their URLs (no local downloading required)
* IIIF protocol is used for image scaling when appropriate

Implementation Details
---------------------

The multimodal functionality is implemented through several key components:

Forms
~~~~~

The ``BaseMultiModalAIBatchForm`` class in ``base_batch_forms.py`` provides the foundation for all multimodal-capable forms:

.. code-block:: python

    class BaseMultiModalAIBatchForm(BaseAIBatchForm):
        """Base form for AI batches with multimodal capabilities."""
        
        # Mode choices for the prompt type
        PROMPT_MODE_CHOICES = [
            ('text_only', 'Text only'),
            ('images_only', 'Images only'),
            ('text_and_images', 'Text + Images')
        ]
        
        prompt_mode = forms.ChoiceField(
            choices=PROMPT_MODE_CHOICES,
            initial='text_only',
            widget=forms.RadioSelect,
            label="Prompt Mode",
            help_text="Choose what to send to the AI service."
        )

AI Clients
~~~~~~~~~

The AI client classes in ``simple_ai_clients.py`` have been extended to handle both file paths and URLs:

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

Task Processing
~~~~~~~~~~~~~~

The task processing logic in ``task_base.py`` has been updated to handle different prompt modes:

.. code-block:: python

    def process_single_ai_request(self, items, client_name, prompt, role_description, 
                                 metadata_field, prompt_mode="text_only"):
        """
        Process an AI request with possible multimodal content (text + images).
        """
        # Get appropriate AI client
        client = self.get_ai_client(client_name)
        
        # Check if this client supports images
        supports_images = hasattr(client, 'supports_images') and client.supports_images
        
        # Process images if needed based on mode
        images = []
        if prompt_mode in ['images_only', 'text_and_images'] and supports_images:
            images = self.collect_document_images(items)
        
        # Build prompt based on mode
        if prompt_mode == 'text_only' or not supports_images:
            result = client.prompt(prompt, role_description)
        elif prompt_mode == 'images_only':
            result = client.prompt_with_images("", role_description, images)
        else:  # text_and_images
            result = client.prompt_with_images(prompt, role_description, images)

User Interface
~~~~~~~~~~~~~

The forms include radio buttons for selecting the prompt mode, providing a clear interface for users to choose how they want to interact with the AI providers.

Page Model Enhancements
~~~~~~~~~~~~~~~~~~~~~~

The ``Page`` model includes a ``get_image_url`` method to retrieve image URLs with optional scaling:

.. code-block:: python

    def get_image_url(self, scale_percent=None):
        """
        Get the URL to the page image with optional scaling.
        """
        try:
            if 'file' not in self.parsed_data or 'imgUrl' not in self.parsed_data['file']:
                return None
                
            image_url = self.parsed_data['file']['imgUrl']
            
            # Return original URL if no scaling requested
            if scale_percent is None:
                return image_url
                
            # Apply scaling via IIIF
            return tk_iiif_url(image_url, image_size=f'pct:{scale_percent}')
        except Exception:
            return None

Fallback Mechanism
~~~~~~~~~~~~~~~~~

For providers that don't support multimodal functionality, the system automatically falls back to text-only mode, ensuring compatibility across all supported AI services.

Usage Examples
-------------

Project AI Query
~~~~~~~~~~~~~~~

To use multimodal functionality in a project query:

1. Navigate to the Project AI Query page
2. Enter your text prompt (if using text)
3. Select the desired prompt mode (Text only, Images only, or Text + Images)
4. Choose documents to include in the query
5. Submit the query

The system will process your request according to the selected mode and return results from the AI provider.

Technical Considerations
-----------------------

Image Size and API Limits
~~~~~~~~~~~~~~~~~~~~~~~~

Different AI providers have varying limits on:

* Maximum number of images per request
* Maximum image size (dimensions and file size)
* Maximum combined request size

The system implements appropriate scaling and selection logic to stay within these limits while maximizing effectiveness.

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~

To optimize performance:

* Images are accessed directly via URL when possible
* IIIF protocol is used for appropriate scaling
* Document pages are limited to 5 per document
* Processing is handled asynchronously via Celery tasks