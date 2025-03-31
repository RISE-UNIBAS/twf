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

