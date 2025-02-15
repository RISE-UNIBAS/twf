"""Celery tasks for processing documents in a project."""
from celery import shared_task
from sphinx.addnodes import document

from twf.clients.simple_ai_clients import AiApiClient
from twf.models import User, Project
from twf.tasks.task_base import start_task, update_task, end_task, fail_task, get_project_and_user


@shared_task(bind=True)
def search_openai_for_docs(self, project_id, user_id, prompt, role_description):
    """Search for information using the OpenAI API for all documents in a project.
    :param self: Celery task
    :param project_id: Project ID
    :param user_id: User ID
    :param prompt: Prompt text
    :param role_description: Role description for the AI model"""

    try:
        project, user = get_project_and_user(project_id, user_id)
        number_of_documents = project.documents.count()
    except ValueError as e:
        raise ValueError(str(e)) from e

    openai_credentials = project.get_credentials('openai')
    task, percentage_complete = start_task(self, project, user_id, text="Starting OpenAI Search...",
                                           title="Project Documents OpenAI Search")

    client = AiApiClient(api='openai',
                         api_key=openai_credentials['api_key'],
                         gpt_role_description=role_description)

    processed_documents = 0
    for document in project.documents.all():
        task, percentage_complete = update_task(self, task, f'OpenAI Search in progress for document {document.id}...',
                                                processed_documents, number_of_documents)

        # Perform OpenAI search for each document
        context = document.get_text()
        prompt = prompt + "\n\n" + "Context:\n" + context
        response, elapsed_time = client.prompt(model=openai_credentials['default_model'],
                                               prompt=prompt)
        response_dict = response.to_dict()
        document.metadata['openai_response'] = response_dict
        document.save(current_user=user)
        processed_documents += 1

    end_task(self, task, 'OpenAI Search Completed.',
             description=f'OpenAI Search for all documents in the project "{project.title}". '
                         f'Processed {processed_documents} documents.')


@shared_task(bind=True)
def search_gemini_for_docs(self, project_id, user_id, prompt, role_description):
    """Search for information using the Gemini API for all documents in a project.
    :param self: Celery task
    :param project_id: Project ID
    :param user_id: User ID
    :param prompt: Prompt text
    :param role_description: Role description for the AI model"""

    try:
        project, user = get_project_and_user(project_id, user_id)
        number_of_documents = project.documents.count()
    except ValueError as e:
        raise ValueError(str(e)) from e

    genai_credentials = project.get_credentials('genai')
    task, percentage_complete = start_task(self, project, user_id, text="Starting Gemini Search...",
                                           title="Project Documents Gemini Search")

    client = AiApiClient(api='genai',
                         api_key=genai_credentials['api_key'],
                         gpt_role_description=role_description)

    processed_documents = 0
    for document in project.documents.all():
        task, percentage_complete = update_task(self, task, f'Gemini Search in progress for document {document.id}...',
                                                processed_documents, number_of_documents)

        context = document.get_text()
        prompt = prompt + "\n\n" + "Context:\n" + context
        response, elapsed_time = client.prompt(model=genai_credentials['default_model'],
                                               prompt=prompt)
        document.metadata['gemini_response'] = response
        document.save(current_user=user)

        processed_documents += 1

    end_task(self, task, 'Gemini Search Completed.',
             description=f'Gemini Search for all documents in the project "{project.title}". '
                         f'Processed {processed_documents} documents.')


@shared_task(bind=True)
def search_claude_for_docs(self, project_id, user_id, prompt, role_description):
    """Search for information using the Claude API for all documents in a project.
    :param self: Celery task
    :param project_id: Project ID
    :param user_id: User ID
    :param prompt: Prompt text
    :param role_description: Role description for the AI model"""

    try:
        project, user = get_project_and_user(project_id, user_id)
        number_of_documents = project.documents.count()
    except ValueError as e:
        raise ValueError(str(e)) from e

    anthropic_credentials = project.get_credentials('anthropic')
    task, percentage_complete = start_task(self, project, user_id, text="Starting Claude Search...",
                                           title="Project Documents Claude Search")

    client = AiApiClient(api='anthropic',
                         api_key=anthropic_credentials['api_key'],
                         gpt_role_description=role_description)

    processed_documents = 0
    for document in project.documents.all():
        task, percentage_complete = update_task(self, task, f'Claude Search in progress for document {document.id}...',
                                                processed_documents, number_of_documents)

        # Perform Gemini search for each document
        context = document.get_text()

        prompt = prompt + "\n\n" + "Context:\n" + context
        response, elapsed_time = client.prompt(model=anthropic_credentials['default_model'],
                                               prompt=prompt)
        document.metadata['claude_response'] = response.to_dict()
        document.save(current_user=user)

        processed_documents += 1

    end_task(self, task, 'Claude Search Completed.',
             description=f'Claude Search for all documents in the project "{project.title}". '
                         f'Processed {processed_documents} documents.')


@shared_task(bind=True)
def search_openai_for_pages(self, project_id, user_id, prompt, role_description):
    pass

@shared_task(bind=True)
def search_gemini_for_pages(self, project_id, user_id, prompt, role_description):
    pass

@shared_task(bind=True)
def search_claude_for_pages(self, project_id, user_id, prompt, role_description):
    pass