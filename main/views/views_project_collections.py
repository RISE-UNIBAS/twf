"""Views for the project collections."""
from django.views.generic import TemplateView

from main.views.views_base import BaseProjectView


class ProjectCollectionsView(BaseProjectView, TemplateView):
    """View for the project collections."""
    template_name = 'main/collections.html'
