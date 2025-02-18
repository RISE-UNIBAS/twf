"""Views for the project setup."""
from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.project.project_forms_batches import DocumentExtractionBatchForm
from twf.views.project.views_project import TWFProjectView


class TWFProjectSetupView(TWFProjectView):
    """View for the project setup."""
    template_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        transkribus_creds = self.get_project().get_credentials('transkribus')
        if transkribus_creds:
            context['transkribus_username'] = transkribus_creds['username']
            context['transkribus_password'] = transkribus_creds['password']

        return context


class TWFProjectTranskribusExtractView(FormView, TWFProjectView):
    """View for the project setup."""
    template_name = 'twf/project/setup/setup_structure.html'
    page_title = 'Project TK Structure'
    form_class = DocumentExtractionBatchForm
    success_url = reverse_lazy('twf:project_tk_structure')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_transkribus_extract_export')
        kwargs['data-message'] = "Are you sure you want to extract your Transkribus export?"

        return kwargs


class TWFProjectExportTestView(TWFProjectView):
    """View for testing the export."""
    template_name = 'twf/project/setup/test_export.html'
    page_title = 'Test Export'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
