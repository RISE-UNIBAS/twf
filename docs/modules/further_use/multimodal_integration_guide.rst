Multimodal Integration Guide
=========================

This guide explains how to integrate multimodal functionality into existing Django applications, using TWF as an example.

Overview
--------

Adding multimodal support (combining text and images) to an existing application involves several components:

1. **Client Layer**: Extending AI clients to handle image inputs
2. **Form Layer**: Adding UI controls for selecting multimodal options
3. **Task Layer**: Adding logic to process images along with text
4. **View Layer**: Connecting the UI with backend processing
5. **Model Layer**: Adding methods to access images from model instances

Integration Steps
---------------

Step 1: Extend AI Clients
~~~~~~~~~~~~~~~~~~~~~~~

First, extend your AI clients to support multimodal inputs:

1. Add a base method for handling images in your abstract client class:

.. code-block:: python

    class AiApiClient:
        """Base class for AI API clients."""
        
        # Flag indicating if this client supports images (override in subclasses)
        supports_images = False
        
        def is_url(self, resource):
            """Check if a resource is a URL or a local file path."""
            return resource.startswith(('http://', 'https://'))
            
        def prompt_with_images(self, prompt_text, role_description, image_sources):
            """Send a prompt with images to the AI provider."""
            raise NotImplementedError("This method should be implemented by subclasses.")

2. Implement provider-specific image handling for each client class:

.. code-block:: python

    class OpenAIClient(AiApiClient):
        """OpenAI client with multimodal support."""
        
        supports_images = True  # Indicate this client supports images
        
        def prompt_with_images(self, prompt_text, role_description, image_sources):
            """OpenAI-specific implementation for handling images."""
            # Implementation details...

Step 2: Create Multimodal Form Controls
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add form controls for selecting multimodal options:

1. Create a base multimodal form class:

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
        
        def __init__(self, *args, **kwargs):
            # Check if this form supports multimodal functionality
            self.multimodal_support = kwargs.pop('multimodal_support', False)
            
            super().__init__(*args, **kwargs)
            
            # Only show the prompt_mode field if multimodal is supported
            if not self.multimodal_support:
                self.fields.pop('prompt_mode', None)

2. Extend provider-specific forms with multimodal support:

.. code-block:: python

    class OpenAIQueryForm(BaseMultiModalAIBatchForm):
        """Form for querying OpenAI models with multimodal support."""
        
        def __init__(self, *args, **kwargs):
            # OpenAI supports multimodal with GPT-4 Vision
            kwargs['multimodal_support'] = True
            super().__init__(*args, **kwargs)

Step 3: Update Task Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Modify your task processing logic to handle multimodal inputs:

1. Update the AI request processing method:

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
            
        # Store the result
        self.store_ai_result(items, result, metadata_field)
        return result

2. Add a method to collect images from documents:

.. code-block:: python

    def collect_document_images(self, items):
        """
        Collect image URLs from documents or collection items.
        
        Args:
            items: A list of document or collection items
            
        Returns:
            A list of image URLs (up to 5 per document)
        """
        images = []
        
        for item in items:
            # Handle different item types
            if hasattr(item, 'pages'):  # This is a document
                # Get up to 5 pages from this document
                pages = item.pages.all().order_by('tk_page_number')[:5]
                for page in pages:
                    if hasattr(page, 'get_image_url'):
                        url = page.get_image_url(scale_percent=50)  # Scale down to 50%
                        if url:
                            images.append(url)
            elif hasattr(item, 'document'):  # This is a collection item
                # Get the document from the collection item
                document = item.document
                if document and hasattr(document, 'pages'):
                    # Get up to 5 pages from this document
                    pages = document.pages.all().order_by('tk_page_number')[:5]
                    for page in pages:
                        if hasattr(page, 'get_image_url'):
                            url = page.get_image_url(scale_percent=50)
                            if url:
                                images.append(url)
                                
        return images

Step 4: Update Task Trigger Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Modify your task trigger functions to accept multimodal parameters:

.. code-block:: python

    def start_query_project_openai(request):
        """
        Trigger an OpenAI query task for the project.
        """
        prompt = request.POST.get('prompt')
        prompt_mode = request.POST.get('prompt_mode', 'text_only')  # Default to text-only
        role_description = request.POST.get('role_description')
        documents = request.POST.getlist('documents')

        return trigger_task(request, query_project_openai,
                          prompt=prompt,
                          role_description=role_description,
                          documents=documents,
                          prompt_mode=prompt_mode)

Step 5: Update Views
~~~~~~~~~~~~~~~~~

Modify your views to handle multimodal form submissions:

1. Update the base AI form view:

.. code-block:: python

    class AIFormView(TWFFormView):
        """
        Base class for views that interact with AI services.
        """
        
        def get_form_kwargs(self):
            """Add multimodal support flag to form kwargs if this provider supports images."""
            kwargs = super().get_form_kwargs()
            
            # Check if this AI provider supports multimodal
            provider = self.get_provider_name()
            kwargs['multimodal_support'] = provider in ['openai', 'claude', 'gemini']
            
            return kwargs
            
        def form_valid(self, form):
            """Process the form submission and start AI task."""
            # Extract form data including prompt mode
            prompt_mode = form.cleaned_data.get('prompt_mode', 'text_only')
            
            # Start the task with prompt mode parameter
            task_func = self.get_task_function()
            task_func(
                # Other parameters...
                prompt_mode=prompt_mode
            )

2. Update your provider-specific views:

.. code-block:: python

    class OpenAIQueryView(AIFormView):
        """View for OpenAI queries with multimodal support."""
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['supports_multimodal'] = True
            context['multimodal_info'] = 'GPT-4 Vision supports images in prompts'
            return context

Step 6: Add Model Methods for Image Access
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add methods to your models to access images:

.. code-block:: python

    class Page(models.Model):
        """Model representing a document page."""
        
        def get_image_url(self, scale_percent=None):
            """
            Get the URL to the page image with optional scaling.
            
            Args:
                scale_percent: Optional percentage for scaling the image
                
            Returns:
                URL to the image, optionally scaled
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

Step 7: Update Templates
~~~~~~~~~~~~~~~~~~~~~

Update your templates to include multimodal controls:

.. code-block:: html

    <!-- Multimodal mode selection -->
    {% if form.prompt_mode %}
    <div class="mb-3">
        <label class="form-label">{{ form.prompt_mode.label }}</label>
        <div class="form-text mb-2">{{ form.prompt_mode.help_text }}</div>
        
        <div class="btn-group" role="group">
            {% for radio in form.prompt_mode %}
            <div class="form-check form-check-inline">
                {{ radio.tag }}
                <label class="form-check-label" for="{{ radio.id_for_label }}">
                    {{ radio.choice_label }}
                </label>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

Best Practices
-------------

1. **Progressive Enhancement**: Add multimodal as an enhancement to existing functionality
2. **Feature Detection**: Always check if a provider supports multimodal before using it
3. **Fallback Mechanisms**: Have fallback to text-only when multimodal isn't supported
4. **Image Optimization**: Optimize images before sending to reduce bandwidth and token usage
5. **UX Considerations**: Make the multimodal options intuitive for users
6. **Testing**: Test thoroughly with different combinations of text and images

Troubleshooting
-------------

Common issues and solutions:

1. **Image Size Limits**: If getting errors about image sizes, implement automatic resizing/scaling
2. **Provider-Specific Formats**: Ensure each provider gets images in its expected format
3. **Missing Image URLs**: Verify image URL extraction is working correctly
4. **Performance Issues**: Limit the number of images per request (5 is usually a good maximum)
5. **API Costs**: Be aware that multimodal requests typically cost more than text-only
6. **CORS Issues**: For URL-based images, ensure they are accessible to the AI provider