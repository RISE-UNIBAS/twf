
from twf.views.project.views_project import TWFProjectView


class TWFProjectSetupView(TWFProjectView):
    """View for the project setup."""
    template_name = 'twf/project/setup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        transkribus_creds = self.get_project().get_credentials('transkribus')
        if transkribus_creds:
            context['transkribus_username'] = transkribus_creds['username']
            context['transkribus_password'] = transkribus_creds['password']

        return context
