
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


class TWFProjectExportTestView(TWFProjectView):
    """View for testing the export."""
    template_name = 'twf/project/setup/test_export.html'
    page_title = 'Test Export'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
