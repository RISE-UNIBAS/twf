Views
======

Overview
--------

Views are the primary interface components of the application. They handle user requests,
process form submissions, and render responses. The views are organized into logical
modules based on their functionality, with each module responsible for a specific
feature area of the application.

TWF uses Django's class-based views extensively. The application defines several base
view classes that provide common functionality:

- **TWFView**: The foundation class for all TWF views, providing project context, navigation,
  and permission handling.
  
- **AIFormView**: A specialized form view for AI interactions, supporting both text-only and 
  multimodal (text + images) workflows.

Each major section of the application (e.g., Documents, Collections, Tags) has its own
view classes that inherit from TWFView and may mix in additional functionality like
AIFormView for AI capabilities.

AI and Multimodal Support
-------------------------

TWF supports AI interactions with several providers (OpenAI, Google Gemini, Anthropic Claude,
and Mistral) through specialized views that extend AIFormView. These views:

1. Verify that valid AI credentials are configured
2. Present appropriate forms for interacting with the AI models
3. Support multimodal workflows for providers that accept both text and images
4. Start asynchronous Celery tasks for processing AI requests
5. Handle task monitoring and result display

For image-based workflows, the system can automatically select relevant images from
the project's documents and include them in the prompt in the appropriate format
for each AI provider.

AIFormView Base Class
~~~~~~~~~~~~~~~~~~~~~

The `AIFormView` base class provides the foundation for all AI-related views, including multimodal support:

.. code-block:: python

    class AIFormView(TWFFormView):
        """
        Base class for views that interact with AI services.
        
        This class provides common functionality for all AI views, including
        multimodal support for combining text and images in prompts.
        """
        
        template_name = "twf/project/query/query.html"
        
        def get_form_kwargs(self):
            """Add multimodal support flag to form kwargs if this provider supports images."""
            kwargs = super().get_form_kwargs()
            
            # Check if this AI provider supports multimodal
            provider = self.get_provider_name()
            kwargs['multimodal_support'] = provider in ['openai', 'claude', 'gemini']
            
            return kwargs
            
        def form_valid(self, form):
            """Process the form submission and start AI task."""
            # Extract form data
            prompt = form.cleaned_data.get('prompt')
            role_description = form.cleaned_data.get('role_description')
            documents = form.cleaned_data.get('documents')
            
            # Get multimodal mode if available
            prompt_mode = form.cleaned_data.get('prompt_mode', 'text_only')
            
            # Start the appropriate AI task with multimodal params
            task_func = self.get_task_function()
            task_func(
                prompt=prompt,
                role_description=role_description,
                documents=documents,
                prompt_mode=prompt_mode
            )
            
            return redirect('project_task_monitor')

Provider-Specific Views
~~~~~~~~~~~~~~~~~~~~~

Each AI provider has its own specific view that extends the base functionality. For a detailed 
explanation of the provider-specific views and multimodal implementation, see:

.. toctree::
   :maxdepth: 1

   views/project_ai.rst

Template Structure
~~~~~~~~~~~~~~~~~~

The AI view templates include support for selecting the multimodal prompt mode:

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

.. toctree::
   :maxdepth: 1
   :caption: Views modules

   views/base.rst
   views/home.rst
   views/project.rst
   views/documents.rst
   views/tags.rst
   views/metadata.rst
   views/dictionaries.rst
   views/collections.rst
   views/export.rst