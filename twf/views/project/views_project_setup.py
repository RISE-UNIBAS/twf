from django.urls import reverse

from twf.views.project.views_project import TWFProjectView


class TWFProjectSetupView(TWFProjectView):
    template_name = 'twf/project/setup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['context_sub_nav'] = {"options": [
            {"url": reverse('twf:project_setup'), "value": "Setup Overview"},
            {"url": reverse('twf:project_tk_export'), "value": "Request Transkribus Export"},
            {"url": reverse('twf:project_tk_structure'), "value": "Extract Transkribus Data"},
            {"url": reverse('twf:project_tk_structure'), "value": "Import Data From JSON File"},
        ]}
        return context