import logging

from celery import shared_task

from twf.models import Project
from twf.clients.simple_ai_clients import AiApiClient

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def ask_chatgpt_task(self, project_id, selection_type, role_description, prompt):
    """Ask ChatGPT to summarize the selected documents in a project.
    :param self: Celery task
    :param project_id: Project ID
    :param selection_type: Type of selection (random, top, bottom)
    :param role_description: Role description for the AI model
    :param prompt: Prompt text
    :return: Task status"""

    try:
        project = Project.objects.get(id=project_id)

        # Gather all the documents/items to ask about
        documents = project.documents.filter(project=project)[:5]
        results = []

        # Ensure API key and role description are being passed correctly
        client = AiApiClient(api='openai',
                             api_key=project.openai_api_key,
                             gpt_role_description=role_description)

        prompt_text = f"Fasse zusammen, was du über die folgendes Dokumente weißt:\n{prompt}"
        for doc in documents:
            response, elapsed_time = client.prompt(model="gpt-4-turbo", prompt=prompt_text)
            result = response.choices[0].message.content
            results.append((doc, result))

        # Save results in metadata or process as needed
        for doc, result in results:
            logger.info(f"Document: {doc}, Result: {result}")

        logger.info(f"Task completed for project: {project_id}")
        return "Completed"

    except Project.DoesNotExist as e:
        error_message = f"Project with id {project_id} does not exist."
        self.update_state(state='FAILURE', meta={'error': error_message})
        raise ValueError(error_message) from e

    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        self.update_state(state='FAILURE', meta={'error': error_message})
        raise ValueError(error_message) from e
