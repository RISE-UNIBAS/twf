Task Triggers Module
=================

The task triggers module provides functions for starting asynchronous tasks from views.

.. automodule:: twf.tasks.task_triggers
   :members:
   :undoc-members:
   :show-inheritance:

AI Task Triggers
---------------

These functions trigger AI-related tasks, including the new multimodal functionality:

.. code-block:: python

    def start_query_project_openai(request):
        """
        Trigger an OpenAI query task for the project.
        
        This function accepts multimodal parameters for combining text and images.
        """
        prompt = request.POST.get('prompt')
        prompt_mode = request.POST.get('prompt_mode', 'text_only')
        role_description = request.POST.get('role_description')
        documents = request.POST.getlist('documents')

        return trigger_task(request, query_project_openai,
                          prompt=prompt,
                          role_description=role_description,
                          documents=documents,
                          prompt_mode=prompt_mode)
                          
    def start_query_project_claude(request):
        """
        Trigger an Anthropic Claude query task for the project.
        
        This function accepts multimodal parameters for combining text and images
        in Claude 3 and above.
        """
        prompt = request.POST.get('prompt')
        prompt_mode = request.POST.get('prompt_mode', 'text_only')
        role_description = request.POST.get('role_description')
        documents = request.POST.getlist('documents')

        return trigger_task(request, query_project_claude,
                          prompt=prompt,
                          role_description=role_description,
                          documents=documents,
                          prompt_mode=prompt_mode)
                          
    def start_query_project_gemini(request):
        """
        Trigger a Google Gemini query task for the project.
        
        This function accepts multimodal parameters as Gemini natively 
        supports multimodal inputs.
        """
        prompt = request.POST.get('prompt')
        prompt_mode = request.POST.get('prompt_mode', 'text_only')
        role_description = request.POST.get('role_description')
        documents = request.POST.getlist('documents')

        return trigger_task(request, query_project_gemini,
                          prompt=prompt,
                          role_description=role_description,
                          documents=documents,
                          prompt_mode=prompt_mode)