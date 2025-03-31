Forms
=====
There are multiple forms in the application. Each form is responsible for handling a
specific part of the application. The main forms are located in the `forms` directory
of the application.

Base Batch Forms
---------------

The base batch forms provide the foundation for batch processing in the application, including AI processing with multimodal support.

.. automodule:: twf.forms.base_batch_forms
   :members:
   :undoc-members:
   :show-inheritance:

Multimodal AI Forms
~~~~~~~~~~~~~~~~~~

The application supports multimodal AI forms that allow combining text and images in AI requests:

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

    # Example of a provider-specific multimodal form
    class OpenAIQueryForm(BaseMultiModalAIBatchForm):
        """Form for querying OpenAI models with multimodal support."""
        
        def __init__(self, *args, **kwargs):
            # OpenAI supports multimodal with GPT-4 Vision
            kwargs['multimodal_support'] = True
            super().__init__(*args, **kwargs)
            
            # Add provider-specific customizations here
            self.fields['model'].choices = [
                ('gpt-4', 'GPT-4'),
                ('gpt-4-vision', 'GPT-4 Vision'),
                ('gpt-3.5-turbo', 'GPT-3.5 Turbo')
            ]

.. toctree::
   :maxdepth: 1
   :caption: Forms modules

   forms/collections.rst
   forms/dictionaries.rst
   forms/documents.rst
   forms/filters.rst
   forms/metadata.rst
   forms/project.rst
   forms/tags.rst