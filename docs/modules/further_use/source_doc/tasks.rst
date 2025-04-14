Tasks
=====

Task Base
---------

The task base module provides the foundation for all asynchronous Celery tasks in the system.

.. automodule:: twf.tasks.task_base
   :members:
   :undoc-members:
   :show-inheritance:

Multimodal Task Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~

The task base module has been extended to support multimodal processing with both text and images:

.. code-block:: python

    def process_single_ai_request(self, items, client_name, prompt, role_description, 
                                 metadata_field, prompt_mode="text_only"):
        """
        Process an AI request with possible multimodal content (text + images).
        
        Args:
            items: A list of document or collection items to process
            client_name: The name of the AI client to use (openai, claude, gemini, mistral)
            prompt: The text prompt to send to the AI
            role_description: The system prompt describing the AI assistant's role
            metadata_field: The field where the result should be stored
            prompt_mode: The mode for sending content - "text_only", "images_only", or "text_and_images"
            
        Returns:
            The response from the AI provider
            
        This method:
        1. Determines if the client supports images
        2. Collects images from documents if needed based on prompt_mode
        3. Calls the appropriate client method based on the mode and capabilities
        4. Stores the result in the specified metadata field
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
            
    def collect_document_images(self, items):
        """
        Collect image URLs from documents or collection items.
        
        Args:
            items: A list of document or collection items
            
        Returns:
            A list of image URLs (up to 5 per document)
        
        This method:
        1. Iterates through all provided items
        2. For each document or collection item with pages
        3. Collects up to 5 image URLs from pages
        4. Returns a list of all collected URLs
        """
        images = []
        
        for item in items:
            if hasattr(item, 'pages'):  # This is a document
                # Get up to 5 pages from this document
                pages = item.pages.all().order_by('tk_page_number')[:5]
                for page in pages:
                    if hasattr(page, 'get_image_url'):
                        url = page.get_image_url(scale_percent=50)  # Scale down to 50%
                        if url:
                            images.append(url)
            elif hasattr(item, 'document'):  # This is a collection item
                # Same logic for collection items that reference documents
                # ...
                
        return images

Document Tasks
--------------

Tasks for document processing.

.. automodule:: twf.tasks.document_tasks
   :members:
   :undoc-members:

Collection Tasks
----------------

Tasks for collection processing.

.. automodule:: twf.tasks.collection_tasks
   :members:
   :undoc-members:

Dictionary Tasks
----------------

Tasks for dictionary processing.

.. automodule:: twf.tasks.dictionary_tasks
   :members:
   :undoc-members:

Project Tasks
-------------

Tasks for project-level operations, including AI queries.

.. automodule:: twf.tasks.project_tasks
   :members:
   :undoc-members:

Multimodal AI Query Tasks
~~~~~~~~~~~~~~~~~~~~~~~~~

The project tasks module includes several tasks for AI queries that support multimodal functionality:

.. code-block:: python

    @shared_task(bind=True, base=BaseTWFTask)
    def query_project_openai(self, project_id, user_id, **kwargs):
        """
        Query an OpenAI model with documents from the project.
        
        Args:
            project_id: The ID of the project
            user_id: The ID of the user making the request
            **kwargs: Additional arguments including:
                - prompt: The text prompt to send
                - role_description: The system prompt
                - documents: List of document IDs to include
                - prompt_mode: The mode ("text_only", "images_only", "text_and_images")
                
        Returns:
            The task info dictionary
            
        This task sends the specified documents along with the prompt to OpenAI,
        using the multimodal capabilities of GPT-4 Vision when images are included.
        """
        # Get the prompt mode (defaults to text_only if not provided)
        prompt_mode = kwargs.pop('prompt_mode', 'text_only')
        
        # Process the request with multimodal support
        self.process_single_ai_request(
            documents, 'openai',
            kwargs['prompt'], kwargs['role_description'], 'openai',
            prompt_mode=prompt_mode
        )

Export Tasks
------------

Tasks for exporting data from the system.

.. automodule:: twf.tasks.export_tasks
   :members:
   :undoc-members:

Structure Tasks
---------------

Tasks for working with document structure.

.. automodule:: twf.tasks.structure_tasks
   :members:
   :undoc-members:

Metadata Tasks
--------------

Tasks for processing metadata.

.. automodule:: twf.tasks.metadata_tasks
   :members:
   :undoc-members:

Tags Tasks
----------

Tasks for tag processing.

.. automodule:: twf.tasks.tags_tasks
   :members:
   :undoc-members: