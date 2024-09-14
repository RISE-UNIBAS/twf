from django.urls import reverse

from twf.views.project.views_project import TWFProjectView


class TWFProjectSetupView(TWFProjectView):
    template_name = 'twf/project/setup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
