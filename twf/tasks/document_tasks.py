"""Celery tasks for processing documents in a project."""
from celery import shared_task

from twf.clients.simple_ai_clients import AiApiClient
from twf.models import Dictionary, User, Project
from twf.tasks.task_base import start_task, update_task, end_task, fail_task


def get_project_and_user(broker, task, project_id, user_id):
    """Get the project and user objects
    :param project_id: Project ID
    :param user_id: User ID
    :return: Project object, User object, number of documents"""
    try:
        project = Project.objects.get(id=project_id)
        user = User.objects.get(id=user_id)
        number_of_documents = project.documents.count()
        return project, user, number_of_documents
    except Project.DoesNotExist as e:
        fail_task(broker, task, f"Project not found: {project_id}")
        raise ValueError(str(e)) from e
    except User.DoesNotExist as e:
        fail_task(broker, task, f"User not found: {user_id}")
        raise ValueError(str(e)) from e
    except Exception as e:
        fail_task(broker, task, str(e))
        raise ValueError(str(e)) from e


def get_text_from_document(document):
    """Get the text from a document
    :param document: Document object
    :return: Text from the document"""
    text = ""
    for page in document.pages.all():
        for element in page.parsed_data['elements']:
            if "text" in element:
                text += element['text'] + "\n"
    return text


@shared_task(bind=True)
def search_openai_for_docs(self, project_id, user_id, prompt, role_description):
    """Search for information using the OpenAI API for all documents in a project.
    :param self: Celery task
    :param project_id: Project ID
    :param user_id: User ID
    :param prompt: Prompt text
    :param role_description: Role description for the AI model"""

    project = Project.objects.get(id=project_id)
    task, percentage_complete = start_task(self, project, user_id, text="Starting OpenAI Search...",
                                           title="Project Documents OpenAI Search")

    project, user, number_of_documents = get_project_and_user(project_id, user_id)
    client = AiApiClient(api='openai',
                         api_key=project.openai_api_key,
                         gpt_role_description=role_description)

    processed_documents = 0
    for document in project.documents.all():
        task, percentage_complete = update_task(self, task, f'OpenAI Search in progress for document {document.id}...',
                                                processed_documents, number_of_documents)

        # Perform OpenAI search for each document
        context = get_text_from_document(document)
        prompt = prompt + "\n\n" + "Context:\n" + context
        response, elapsed_time = client.prompt(model="gpt-4-turbo",
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
    project = Project.objects.get(id=project_id)
    task, percentage_complete = start_task(self, project, user_id, text="Starting Gemini Search...",
                                           title="Project Documents Gemini Search")

    project, user, number_of_documents = get_project_and_user(self, task, project_id, user_id)
    client = AiApiClient(api='genai',
                         api_key=project.gemini_api_key,
                         gpt_role_description=role_description)

    processed_documents = 0
    for document in project.documents.all():
        task, percentage_complete = update_task(self, task, f'Gemini Search in progress for document {document.id}...',
                                                processed_documents, number_of_documents)

        context = get_text_from_document(document)
        prompt = prompt + "\n\n" + "Context:\n" + context
        response, elapsed_time = client.prompt(model="gemini-1.5-flash",
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

    project = Project.objects.get(id=project_id)
    task, percentage_complete = start_task(self, project, user_id, text="Starting Claude Search...",
                                           title="Project Documents Claude Search")

    project, user, number_of_documents = get_project_and_user(self, task, project_id, user_id)
    client = AiApiClient(api='anthropic',
                         api_key=project.claude_api_key,
                         gpt_role_description=role_description)

    processed_documents = 0
    for document in project.documents.all():
        task, percentage_complete = update_task(self, task, f'Claude Search in progress for document {document.id}...',
                                                processed_documents, number_of_documents)

        # Perform Gemini search for each document
        context = get_text_from_document(document)

        prompt = prompt + "\n\n" + "Context:\n" + context
        response, elapsed_time = client.prompt(model="claude-3-5-sonnet-20240620",
                                               prompt=prompt)
        document.metadata['claude_response'] = response.to_dict()
        document.save(current_user=user)

        processed_documents += 1

    end_task(self, task, 'Claude Search Completed.',
             description=f'Claude Search for all documents in the project "{project.title}". '
                         f'Processed {processed_documents} documents.')
