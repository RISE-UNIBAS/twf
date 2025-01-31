"""Base views for all views."""
from abc import ABC, abstractmethod

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse
from django.views.generic import TemplateView
from django.conf import settings
from twf.models import Project


class TWFView(TemplateView, ABC):
    """Base view for all views."""
    project_required = True
    page_title = None

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
                'navigation': {
                    'items': self.get_navigation_items(),
                },
                'context_nav': {
                    'groups': self.get_sub_navigation()
                },
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
