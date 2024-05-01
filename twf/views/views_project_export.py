"""Views for the project export."""
from django.views.generic import TemplateView

from twf.views.views_base import BaseProjectView


class ProjectExportView(BaseProjectView, TemplateView):
    """View for the project export."""
    template_name = 'twf/export.html'
