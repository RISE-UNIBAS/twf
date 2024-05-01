"""Views for project setup."""
from django.views.generic import FormView

from main.forms import GoogleDocsSettingsForm
from main.views.views_base import BaseProjectView


class ProjectSetupView(FormView, BaseProjectView):
    """View for project setup. All actual functions are handled by ajax calls."""
    template_name = 'main/project.html'
    form_class = GoogleDocsSettingsForm

    def get_form_kwargs(self):
        """Pass the project instance to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_project()
        return kwargs

    def get_context_data(self, **kwargs):
        """Add the project and tag types to the context."""
        context = super().get_context_data(**kwargs)
        context.update({'project': self.get_project(), 'tag_types': self.get_tag_types()})
        return context
