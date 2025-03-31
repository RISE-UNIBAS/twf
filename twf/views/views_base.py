"""Base views for all views."""
from abc import ABC, abstractmethod

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from django.conf import settings
from twf.models import Project


class TWFView(TemplateView, ABC):
    """Base view for all views."""
    project_required = True
    page_title = None
    navigation_anchor = None
    show_context_help = True  # Flag to control visibility of the context help button

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.page_title is None:
            self.page_title = kwargs.get('page_title', None)

    def dispatch(self, request, *args, **kwargs):
        if self.project_required:
            project = self.get_project()
            if project is None:
                messages.error(request, 'No project is set. Select a project first')
                return redirect('twf:home')  # Redirect if no project is set
        return super().dispatch(request, *args, **kwargs)

    def is_project_set(self):
        """Check if a project is set."""
        return self.s_is_project_set(self.request)

    @staticmethod
    def s_is_project_set(request):
        """Check if a project is set."""
        return request.session.get('project_id', None) is not None

    def get_project(self):
        """Get the project."""
        return self.s_get_project(self.request)

    @staticmethod
    def s_get_project(request):
        """Get the project."""
        project = None
        if TWFView.s_is_project_set(request):
            project_id = request.session.get('project_id')
            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                request.session['project_id'] = None
        return project

    def get_breadcrumbs(self):
        """Get the breadcrumbs."""
        breadcrumbs = [
            {'url': reverse('twf:home'), 'value': '<i class="fas fa-home"></i>'},
        ]
        if len(self.get_navigation_items()) > self.get_navigation_index() > 0:
            breadcrumbs.append(self.get_navigation_items()[self.get_navigation_index()])

        # Only add current page if it has a `page_title` and isn't already part of the nav
        if hasattr(self, 'page_title') and self.page_title != breadcrumbs[-1]["value"]:
            breadcrumbs.append({
                "value": self.page_title,
                "url": self.request.path,
            })

        return breadcrumbs

    def get_navigation_items(self):
        """Get the navigation items."""
        if not self.is_project_set():
            return [
                {'url': reverse('twf:home'), 'value': 'Home', 'active': True},
            ]

        nav = [
            {'url': reverse('twf:home'), 'value': 'Home'},
            {'url': reverse('twf:project_overview'), 'value': 'Project'},
            {'url': reverse('twf:documents_overview'), 'value': 'Documents'},
            {'url': reverse('twf:tags_overview'), 'value': 'Tags'},
            {'url': reverse('twf:metadata_overview'), 'value': 'Metadata'},
            {'url': reverse('twf:dictionaries_overview'), 'value': 'Dictionaries'},
            {'url': reverse('twf:collections'), 'value': 'Collections'},
            {'url': reverse('twf:export_overview'), 'value': 'Import/Export'},
        ]
        return nav

    @abstractmethod
    def get_sub_navigation(self):
        """Get the sub navigation."""
        pass

    @abstractmethod
    def get_navigation_index(self):
        """Get the index of the navigation item."""
        pass

    def get_context_data(self, **kwargs):
        """Add the project and tag types to the context."""
        context = super().get_context_data(**kwargs)

        context.update(
            {
                'page_title': self.page_title,
                'project_set': self.is_project_set(),
                'project': self.get_project(),
                'breadcrumbs': self.get_breadcrumbs(),
                'navigation': {
                    'items': self.get_navigation_items(),
                },
                'context_nav': {
                    'groups': self.get_sub_navigation()
                },
                'navigation_anchor': self.navigation_anchor,
                'show_context_help': self.show_context_help,  # Add the flag to the context
                'version': settings.TWF_VERSION
            }
        )

        if len(context['navigation']['items']) > self.get_navigation_index():
            context['navigation']['items'][self.get_navigation_index()]['active'] = True
        return context


def help_content(request, view_name):
    template_path = f"twf/help/{view_name}.html"
    try:
        template = get_template(template_path)
        return HttpResponse(template.render({}, request))
    except TemplateDoesNotExist:
        return HttpResponse("<p>Help content not found.</p>", status=404)


class AIFormView(FormView):
    """
    Base view for AI interaction forms.
    
    This view provides a foundation for all AI-related forms in the application,
    including multimodal forms that can process both text and images. It handles:
    
    1. Proper form initialization with project context
    2. AI credential validation 
    3. Task URL and confirmation message setup
    
    When extended by specific AI provider views (like TWFProjectOpenAIView),
    it configures the appropriate form with the project's credentials and
    starts the correct Celery task when the form is submitted.
    
    Attributes:
        start_url (str): The URL to start the AI task
        message (str): Confirmation message to display before starting the task
    """
    start_url = None
    message = None

    def get_form_kwargs(self):
        """
        Prepare keyword arguments for the form initialization.
        
        This method extends the standard form kwargs with project-specific
        information and AI task configuration parameters. These kwargs are
        passed to the form's __init__ method.
        
        Returns:
            dict: Dictionary of keyword arguments for the form, including:
                - project: The current Project object
                - data-start-url: URL to start the AI task
                - data-message: Confirmation message to display
        """
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = self.start_url
        kwargs['data-message'] = self.message

        return kwargs

    def get_ai_credentials(self, client_name):
        """
        Get the AI credentials for a specific provider from the project.
        
        Args:
            client_name (str): The name of the AI provider to get credentials for
                              ('openai', 'genai', 'anthropic', or 'mistral')
                              
        Returns:
            dict: A dictionary containing the credentials for the specified provider,
                 typically including 'api_key' and 'default_model' keys
        """
        project = self.get_project()
        if project is None:
            return {}
        return project.get_credentials(client_name)

    def has_ai_credentials(self, client_name):
        """
        Check if valid AI credentials are set for a specific provider.
        
        This method verifies that both an API key and a default model are
        configured for the specified AI provider.
        
        Args:
            client_name (str): The name of the AI provider to check
                              ('openai', 'genai', 'anthropic', or 'mistral')
                              
        Returns:
            bool: True if both api_key and default_model are set, False otherwise
        """
        creds = self.get_ai_credentials(client_name)
        if creds is None:
            return False

        if "api_key" in creds and creds["api_key"]:
            if "default_model" in creds and creds["default_model"]:
                return True

        return False
