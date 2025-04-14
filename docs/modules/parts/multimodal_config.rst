Multimodal Configuration
========================

This page documents the configuration options and settings for the multimodal functionality in TWF.

Default Settings
----------------

The multimodal functionality has the following default settings:

.. code-block:: python

    # Default multimodal settings
    MULTIMODAL_DEFAULTS = {
        'max_images_per_document': 5,      # Maximum number of images to include per document
        'default_scaling_percent': 50,     # Default scaling percentage for images
        'default_prompt_mode': 'text_only', # Default prompt mode
        'enable_auto_selection': True,     # Whether to enable automatic image selection
        'max_total_images': 10             # Maximum total images across all documents
    }

These settings can be overridden in your project settings.py file.

Provider-Specific Settings
------------------------

Each AI provider has specific settings for multimodal functionality:

OpenAI Settings
~~~~~~~~~~~~~~~

.. code-block:: python

    # OpenAI multimodal settings
    OPENAI_MULTIMODAL_SETTINGS = {
        'supported_models': ['gpt-4-vision-preview', 'gpt-4-turbo-2024-04-09'],
        'max_tokens_per_request': 4096,
        'max_image_size_mb': 20,
        'supports_text_and_images': True,
        'supports_images_only': True
    }

Claude Settings
~~~~~~~~~~~~~~~

.. code-block:: python

    # Claude multimodal settings
    CLAUDE_MULTIMODAL_SETTINGS = {
        'supported_models': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
        'max_tokens_per_request': 4096,
        'max_image_size_mb': 10,
        'supports_text_and_images': True,
        'supports_images_only': True
    }

Gemini Settings
~~~~~~~~~~~~~~~

.. code-block:: python

    # Gemini multimodal settings
    GEMINI_MULTIMODAL_SETTINGS = {
        'supported_models': ['gemini-pro-vision', 'gemini-1.5-pro'],
        'max_tokens_per_request': 8192,
        'max_image_size_mb': 15,
        'supports_text_and_images': True,
        'supports_images_only': True
    }

Mistral Settings
~~~~~~~~~~~~~~~~

.. code-block:: python

    # Mistral multimodal settings
    MISTRAL_MULTIMODAL_SETTINGS = {
        'supported_models': ['mistral-large-latest'],
        'max_tokens_per_request': 4096,
        'max_image_size_mb': 5,
        'max_images_per_request': 2,
        'supports_text_and_images': True,
        'supports_images_only': True
    }

Image Scaling Options
---------------------

When using the IIIF protocol for image scaling, the following options are available:

.. code-block:: python

    # IIIF scaling options
    IIIF_SCALING_OPTIONS = {
        'pct': {
            'description': 'Scale by percentage',
            'values': [10, 25, 50, 75, 100]
        },
        'w': {
            'description': 'Scale by width in pixels',
            'values': [512, 768, 1024, 1536, 2048]
        },
        'h': {
            'description': 'Scale by height in pixels',
            'values': [512, 768, 1024, 1536, 2048]
        },
        'max': {
            'description': 'Scale by maximum dimension in pixels',
            'values': [512, 768, 1024, 1536, 2048]
        }
    }

The default scaling method is 'pct:50' (50% of original size).

Form Configuration
------------------

Multimodal form configuration options:

.. code-block:: python

    # Multimodal form configuration
    MULTIMODAL_FORM_CONFIG = {
        'show_mode_selection': True,      # Whether to show the mode selection controls
        'show_scaling_options': False,    # Whether to show image scaling options
        'show_image_preview': True,       # Whether to show image previews
        'max_selectable_documents': 5,    # Maximum number of documents that can be selected
        'default_role_description': 'You are a helpful assistant analyzing documents.'
    }

Environment Variables
---------------------

The following environment variables can be used to configure the multimodal functionality:

* ``TWF_MULTIMODAL_ENABLED``: Enable or disable multimodal functionality entirely (default: "true")
* ``TWF_MAX_IMAGES_PER_DOC``: Maximum images per document (default: "5")
* ``TWF_DEFAULT_SCALING``: Default scaling percentage (default: "50")
* ``TWF_MAX_TOTAL_IMAGES``: Maximum total images across all documents (default: "10")

URL Configuration
-----------------

The default URL configuration for multimodal views:

.. code-block:: python

    # URLs for multimodal views
    urlpatterns = [
        path('project/ai/query/openai/', OpenAIQueryView.as_view(), name='project_query_openai'),
        path('project/ai/query/claude/', ClaudeQueryView.as_view(), name='project_query_claude'),
        path('project/ai/query/gemini/', GeminiQueryView.as_view(), name='project_query_gemini'),
        path('project/ai/query/mistral/', MistralQueryView.as_view(), name='project_query_mistral'),
    ]

Project-Level Configuration
-------------------------

Project model configuration for multimodal functionality:

.. code-block:: python

    class Project(models.Model):
        # Existing fields...
        
        # Multimodal configuration
        conf_multimodal = models.JSONField(
            default=dict,
            blank=True,
            help_text="Configuration for multimodal AI functionality"
        )
        
        def get_multimodal_config(self):
            """Get the multimodal configuration for this project."""
            defaults = MULTIMODAL_DEFAULTS.copy()
            project_config = self.conf_multimodal or {}
            defaults.update(project_config)
            return defaults