"""Base views for all views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView

from main.models import PageTag, Dictionary, Project


class BaseView(LoginRequiredMixin, View):
    """Base view for all views."""

    login_url = '/login/'  # Redirect to login page if not authenticated
    redirect_field_name = 'redirect_to'

    def get_project(self):
        """Get the project from the URL."""
        return Project.objects.get(pk=self.kwargs.get('pk'))

    def get_dictionaries(self):
        """Get all dictionaries."""
        return Dictionary.objects.all()

    def get_excluded_types(self):
        """Get the types that should be excluded from the tag types."""
        excluded_types = ['date', 'print_date']
        try:
            excluded_types.extend(self.get_project().ignored_tag_types["ignored"])
        except KeyError:
            pass
        return excluded_types

    def get_tag_types(self):
        """Get all tag types that are not excluded."""
        excluded_types = self.get_excluded_types()

        unassigned_tags = PageTag.objects.filter(page__document__project=self.get_project(),
                                                 dictionary_entry=None,
                                                 is_parked=False).exclude(variation_type__in=excluded_types)

        variation_types = unassigned_tags.values_list('variation_type', flat=True).order_by('variation_type').distinct()
        return variation_types


class BaseProjectView(BaseView):
    """Base view for all project views."""
    template_name = None

    def get_context_data(self, **kwargs):
        """Add the project and tag types to the context."""
        context = {'project': self.get_project(),
                   'tag_types': self.get_tag_types()}
        return context


class BaseProjectListView(BaseView, ListView):
    """Base view for all project list views."""

    def get_context_data(self, **kwargs):
        """Add the project and tag types to the context."""
        context = super().get_context_data(**kwargs)
        context.update({'project': self.get_project(),
                        'tag_types': self.get_tag_types()})
        return context
