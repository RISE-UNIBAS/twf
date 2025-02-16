"""Celery tasks for processing documents in a project."""
from celery import shared_task
from twf.models import Page
from twf.tasks.task_base import BaseTWFTask


@shared_task(bind=True, base=BaseTWFTask)
def search_openai_for_docs(self, project_id, user_id, **kwargs):
    self.validate_task_parameters(kwargs, ['prompt', 'role_description'])
    self.process_ai_request(self.project.documents.all(), 'openai',
                            kwargs['prompt'], kwargs['role_description'], 'openai')


@shared_task(bind=True, base=BaseTWFTask)
def search_gemini_for_docs(self, project_id, user_id, **kwargs):
    self.validate_task_parameters(kwargs, ['prompt', 'role_description'])
    self.process_ai_request(self.project.documents.all(), 'genai',
                            kwargs['prompt'], kwargs['role_description'], 'gemini')


@shared_task(bind=True, base=BaseTWFTask)
def search_claude_for_docs(self, project_id, user_id, **kwargs):
    self.validate_task_parameters(kwargs, ['prompt', 'role_description'])
    self.process_ai_request(self.project.documents.all(), 'anthropic',
                            kwargs['prompt'], kwargs['role_description'], 'claude')


@shared_task(bind=True, base=BaseTWFTask)
def search_openai_for_pages(self, project_id, user_id, **kwargs):
    self.validate_task_parameters(kwargs, ['prompt', 'role_description'])
    pages = Page.objects.filter(document__project=self.project, is_ignored=False)
    self.process_ai_request(pages, 'openai', kwargs['prompt'], kwargs['role_description'], 'openai')


@shared_task(bind=True, base=BaseTWFTask)
def search_gemini_for_pages(self, project_id, user_id, **kwargs):
    self.validate_task_parameters(kwargs, ['prompt', 'role_description'])
    pages = Page.objects.filter(document__project=self.project, is_ignored=False)
    self.process_ai_request(pages, 'genai', kwargs['prompt'], kwargs['role_description'], 'gemini')


@shared_task(bind=True, base=BaseTWFTask)
def search_claude_for_pages(self, project_id, user_id, **kwargs):
    self.validate_task_parameters(kwargs, ['prompt', 'role_description'])
    pages = Page.objects.filter(document__project=self.project, is_ignored=False)
    self.process_ai_request(pages, 'anthropic', kwargs['prompt'], kwargs['role_description'], 'claude')
