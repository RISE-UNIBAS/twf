""" Celery tasks for creating collections """

from celery import shared_task

from twf.models import CollectionItem
from twf.tasks.task_base import BaseTWFTask


@shared_task(bind=True, base=BaseTWFTask)
def create_collection(self, project_id, user_id, **kwargs):
    """Create a collection for a project"""
    self.validate_task_parameters(kwargs, ["collection_name", "collection_description"])

    self.end_task()


@shared_task(bind=True, base=BaseTWFTask)
def search_ai_for_collection(self, project_id, user_id, **kwargs):
    """
    Unified task for AI batch processing of collection items.

    Supports any AI provider through the generic AI client.

    Args:
        project_id: Project ID
        user_id: User ID
        **kwargs: Must include:
            - collection_id: ID of the collection to process
            - ai_provider: Provider key ('openai', 'genai', 'anthropic', 'mistral', etc.)
            - model: Model name to use
            - prompt: The prompt template
            - role_description: System role description
    """
    self.validate_task_parameters(
        kwargs, ["collection_id", "ai_provider", "model", "prompt", "role_description"]
    )

    collection = self.project.collections.get(id=kwargs.get("collection_id"))
    provider = kwargs.get("ai_provider")

    self.process_ai_request(
        collection.items.all(),
        provider,
        kwargs["prompt"],
        kwargs["role_description"],
        provider,
        model=kwargs.get("model"),
    )


@shared_task(bind=True, base=BaseTWFTask)
def search_ai_for_collection_item(self, project_id, user_id, **kwargs):
    """
    Unified task for AI request (supervised) processing of a single collection item.

    Supports any AI provider through the generic AI client.

    Args:
        project_id: Project ID
        user_id: User ID
        **kwargs: Must include:
            - item_id: ID of the collection item to process
            - ai_provider: Provider key ('openai', 'genai', 'anthropic', 'mistral', etc.)
            - model: Model name to use
            - prompt: The prompt template
            - role_description: System role description
    """
    self.validate_task_parameters(
        kwargs, ["item_id", "ai_provider", "model", "prompt", "role_description"]
    )

    item = CollectionItem.objects.get(id=kwargs.get("item_id"))
    provider = kwargs.get("ai_provider")

    self.process_ai_request(
        [item],
        provider,
        kwargs["prompt"],
        kwargs["role_description"],
        provider,
        model=kwargs.get("model"),
    )
