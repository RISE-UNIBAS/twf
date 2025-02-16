""" Celery tasks for creating collections """
from celery import shared_task

from twf.models import CollectionItem
from twf.tasks.task_base import BaseTWFTask


@shared_task(bind=True, base=BaseTWFTask)
def create_collection(self, project_id, user_id, **kwargs):
    """ Create a collection for a project """
    self.validate_task_parameters(kwargs,
                                  ['collection_name', 'collection_description'])

    self.end_task()


@shared_task(bind=True, base=BaseTWFTask)
def search_openai_for_collection(self, project_id, user_id, **kwargs):
    """ Search for information using the OpenAI API for a collection """
    self.validate_task_parameters(kwargs,
                                  ['collection_id', 'prompt', 'role_description'])

    collection = self.project.collections.get(id=kwargs.get('collection_id'))
    self.process_ai_request(collection.items.all(), 'openai',
                            kwargs['prompt'], kwargs['role_description'], 'openai')


@shared_task(bind=True, base=BaseTWFTask)
def search_gemini_for_collection(self, project_id, user_id, **kwargs):
    """ Search for information using the Gemini API for a collection """
    self.validate_task_parameters(kwargs,
                                  ['collection_id', 'prompt', 'role_description'])

    collection = self.project.collections.get(id=kwargs.get('collection_id'))
    self.process_ai_request(collection.items.all(), 'genai',
                            kwargs['prompt'], kwargs['role_description'], 'gemini')


@shared_task(bind=True, base=BaseTWFTask)
def search_claude_for_collection(self, project_id, user_id, **kwargs):
    """ Search for information using the Claude API for a collection """
    self.validate_task_parameters(kwargs,
                                  ['collection_id', 'prompt', 'role_description'])

    collection = self.project.collections.get(id=kwargs.get('collection_id'))
    self.process_ai_request(collection.items.all(), 'anthropic',
                            kwargs['prompt'], kwargs['role_description'], 'claude')


@shared_task(bind=True, base=BaseTWFTask)
def search_openai_for_collection_item(self, project_id, user_id, **kwargs):
    """ Search for information using the OpenAI API for a collection """
    self.validate_task_parameters(kwargs,
                                  ['item_id', 'prompt', 'role_description'])

    item = CollectionItem.objects.get(id=kwargs.get('item_id'))
    self.process_ai_request([item], 'openai',
                            kwargs['prompt'], kwargs['role_description'], 'openai')


@shared_task(bind=True, base=BaseTWFTask)
def search_gemini_for_collection_item(self, project_id, user_id, **kwargs):
    """ Search for information using the Gemini API for a collection """
    self.validate_task_parameters(kwargs,
                                  ['item_id', 'prompt', 'role_description'])

    item = CollectionItem.objects.get(id=kwargs.get('item_id'))
    self.process_ai_request([item], 'genai',
                            kwargs['prompt'], kwargs['role_description'], 'gemini')


@shared_task(bind=True, base=BaseTWFTask)
def search_claude_for_collection_item(self, project_id, user_id, **kwargs):
    """ Search for information using the Claude API for a collection """
    self.validate_task_parameters(kwargs,
                                  ['item_id', 'prompt', 'role_description'])

    item = CollectionItem.objects.get(id=kwargs.get('item_id'))
    self.process_ai_request([item], 'anthropic',
                            kwargs['prompt'], kwargs['role_description'], 'claude')
