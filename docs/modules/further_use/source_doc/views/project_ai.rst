Project AI Views
==============

The project AI views provide the interface for users to interact with various AI providers, including the new multimodal functionality.

Overview
--------

The project AI views extend the base ``AIFormView`` class to provide specific functionality for each AI provider. These views support both text-only and multimodal (text + images) interactions.

Common Features
--------------

All project AI views share these common features:

1. **Provider Selection**: Each view is dedicated to a specific AI provider (OpenAI, Claude, Gemini, Mistral)
2. **API Validation**: The views check that valid API credentials are configured for the selected provider
3. **Form Handling**: The views present appropriate forms for configuring the AI request
4. **Task Management**: The views trigger asynchronous Celery tasks to process the AI requests
5. **Result Handling**: After task completion, the results are displayed to the user

Multimodal Support
-----------------

For providers that support multimodal functionality, the views include:

1. **Mode Selection**: Radio buttons to choose between text-only, images-only, or text+images modes
2. **Automatic Image Selection**: The system automatically selects appropriate images from chosen documents
3. **Provider-Specific Context**: Information about which providers support multimodal and what limitations apply
4. **Task Parameter Passing**: The views pass appropriate multimodal parameters to the Celery tasks

Implementation
-------------

The key views for AI functionality include:

OpenAI Query View
~~~~~~~~~~~~~~~~

.. code-block:: python

    class OpenAIQueryView(AIFormView):
        """View for OpenAI queries with multimodal support."""
        form_class = OpenAIQueryForm
        template_name = "twf/project/query/openai.html"
        permission_required = "project.can_query_ai"
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['provider_name'] = 'OpenAI'
            context['supports_multimodal'] = True
            context['multimodal_info'] = 'GPT-4 Vision supports images in prompts'
            return context
            
        def get_task_function(self):
            return start_query_project_openai

Claude Query View
~~~~~~~~~~~~~~~

.. code-block:: python

    class ClaudeQueryView(AIFormView):
        """View for Anthropic Claude queries with multimodal support."""
        form_class = ClaudeQueryForm
        template_name = "twf/project/query/claude.html"
        permission_required = "project.can_query_ai"
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['provider_name'] = 'Claude'
            context['supports_multimodal'] = True
            context['multimodal_info'] = 'Claude 3 supports images in prompts'
            return context
            
        def get_task_function(self):
            return start_query_project_claude

Gemini Query View
~~~~~~~~~~~~~~~

.. code-block:: python

    class GeminiQueryView(AIFormView):
        """View for Google Gemini queries with multimodal support."""
        form_class = GeminiQueryForm
        template_name = "twf/project/query/gemini.html"
        permission_required = "project.can_query_ai"
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['provider_name'] = 'Gemini'
            context['supports_multimodal'] = True
            context['multimodal_info'] = 'Gemini natively supports multimodal inputs'
            return context
            
        def get_task_function(self):
            return start_query_project_gemini

Mistral Query View
~~~~~~~~~~~~~~~~

.. code-block:: python

    class MistralQueryView(AIFormView):
        """View for Mistral queries with limited multimodal support."""
        form_class = MistralQueryForm
        template_name = "twf/project/query/mistral.html"
        permission_required = "project.can_query_ai"
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['provider_name'] = 'Mistral'
            # Only some Mistral models support multimodal
            context['supports_multimodal'] = self.project.get_mistral_model() in ["mistral-large-latest"]
            context['multimodal_info'] = 'Only available with Mistral Large'
            return context
            
        def get_task_function(self):
            return start_query_project_mistral

Template Integration
------------------

The templates for the AI views include common elements for multimodal support:

.. code-block:: html

    <!-- Multimodal mode selection - only visible for providers that support images -->
    {% if supports_multimodal %}
    <div class="card mb-3">
        <div class="card-header">
            <h5>Prompt Mode</h5>
        </div>
        <div class="card-body">
            <div class="form-group">
                <div class="form-text mb-2">{{ multimodal_info }}</div>
                
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
        </div>
    </div>
    {% endif %}

Usage Flow
---------

The typical flow for using the multimodal AI features through these views:

1. User navigates to the appropriate AI provider view (e.g., OpenAI, Claude)
2. User enters their prompt text (if using text mode)
3. User selects prompt mode (Text only, Images only, or Text + Images)
4. User selects documents to include in the query
5. User submits the form
6. View triggers the appropriate task with multimodal parameters
7. Task processes the request asynchronously
8. Results are displayed to the user in the task monitor