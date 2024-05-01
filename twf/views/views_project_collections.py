"""Views for the project collections."""
from django.views.generic import TemplateView

from twf.views.views_base import BaseProjectView


class ProjectCollectionsView(BaseProjectView, TemplateView):
    """View for the project collections."""
    template_name = 'twf/collections.html'
