"""Celery tasks for processing documents in a project."""
import logging
from celery import shared_task
from twf.models import Page
from twf.tasks.task_base import BaseTWFTask

logger = logging.getLogger(__name__)


@shared_task(bind=True, base=BaseTWFTask)
def search_ai_for_docs(self, project_id, user_id, **kwargs):
    """
    Unified task for AI batch processing of documents.

    Supports any AI provider through the generic AI client.

    Args:
        project_id: Project ID
        user_id: User ID
        **kwargs: Must include:
            - ai_provider: Provider key ('openai', 'genai', 'anthropic', 'mistral', etc.)
            - model: Model name to use
            - prompt: The prompt template
            - role_description: System role description
            - prompt_mode (optional): Prompt mode for multimodal
            - request_level (optional): Request level
    """
    self.validate_task_parameters(kwargs, ['ai_provider', 'model', 'prompt', 'role_description'])

    provider = kwargs.get('ai_provider')
    model = kwargs.get('model')
    prompt_mode = kwargs.get('prompt_mode', 'text_only')

    # Get document count and filter active documents if needed
    documents = self.project.documents.all()
    doc_count = documents.count()

    # Update task with document count information
    if self.twf_task:
        self.twf_task.text += f"Found {doc_count} documents to process with {provider}.\n"
        self.twf_task.save(update_fields=["text"])

    # Process all documents with the specified provider
    self.process_ai_request(
        documents,
        provider,
        kwargs['prompt'],
        kwargs['role_description'],
        provider,
        prompt_mode=prompt_mode,
        model=model
    )

    return {
        'status': 'completed',
        'documents_processed': doc_count
    }
