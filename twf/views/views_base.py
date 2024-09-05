"""Base views for all views."""
from abc import ABC, abstractmethod

from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now, timedelta
from django.views.generic import TemplateView

from twf.forms.user_forms import LoginForm, ChangePasswordForm
from twf.models import Project, Document, Page, Dictionary, DictionaryEntry, PageTag, Variation, DateVariation, \
    TWF_GROUPS


class TWFView(TemplateView, ABC):
    """Base view for all views."""
    page_title = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.page_title is None:
            self.page_title = kwargs.get('page_title', None)

    def is_project_set(self):
        """Check if a project is set."""
        return self.s_is_project_set(self.request)

    @staticmethod
    def s_is_project_set(request):
        return request.session.get('project_id', None) is not None

    def get_project(self):
        return self.s_get_project(self.request)

    @staticmethod
    def s_get_project(request):
        project = None
        if TWFView.s_is_project_set(request):
            project_id = request.session.get('project_id')
            project = Project.objects.get(pk=project_id)
        return project

    def get_navigation_items(self):
        """Get the navigation items."""
        if not self.is_project_set():
            return [
                {'url': reverse('twf:home'), 'value': 'Home', 'active': True},
            ]

        nav = [
            {'url': reverse('twf:home'), 'value': 'Home'},
            {'url': reverse('twf:project_overview'), 'value': 'Project'},
            {'url': reverse('twf:tags_overview'), 'value': 'Tags'},
            {'url': reverse('twf:metadata_overview'), 'value': 'Metadata'},
            {'url': reverse('twf:dictionaries'), 'value': 'Dictionaries'},
        ]
        return nav

    def get_user_options(self):
        """Get the user options."""
        user = self.request.user

        if user.is_authenticated:
            return [
                {'url': reverse('twf:user_overview'), 'value': 'Overview'},
                {'url': reverse('twf:user_change_password'), 'value': 'Change Password'},
                {'url': reverse('twf:user_management'), 'value': 'User Management'},
                {'url': reverse('twf:user_logout'), 'value': 'Logout'},
            ]

        return [
            {'url': reverse('twf:login'), 'value': 'Login'},
        ]

    @abstractmethod
    def get_sub_navigation(self):
        """Get the sub navigation."""
        pass

    def get_context_data(self, **kwargs):
        """Add the project and tag types to the context."""
        context = super().get_context_data(**kwargs)

        project = None
        if self.is_project_set():
            project_id = self.request.session.get('project_id', None)
            project = Project.objects.get(pk=project_id)
            context['project'] = project

        context.update(
            {
                'page_title': self.page_title,
                'project_set': self.is_project_set(),
                'project': project,
                'navigation': {
                    'items': self.get_navigation_items(),
                },
                'context_nav': {
                    'groups': self.get_sub_navigation()
                }
            }
        )
        return context


class TWFHomeView(TWFView):
    """Base view for the home view."""
    template_name = 'twf/base/home.html'

    def get_sub_navigation(self):
        """Get the sub navigation."""
        sub_nav = []
        if self.request.user.is_authenticated:
            user_projects = self.request.user.profile.get_projects()
            proj_nav = []
            for proj in user_projects:
                proj_nav.append({'url': reverse('twf:project_select', args=[proj.id]),
                                 'value': proj.title})

            sub_nav.append({'name': 'Select Project',
                            'options': proj_nav})

        sub_nav.append({
            'name': 'User Options',
            'options': self.get_user_options()
        })

        return sub_nav

    def get_context_data(self, **kwargs):
        """Add the active item to the navigation."""
        context = super().get_context_data(**kwargs)
        context['navigation']['items'][0]['active'] = True
        return context

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.page_title is None:
            self.page_title = kwargs.get('page_title', 'Home View')


class TWFHomeLoginView(TWFHomeView, LoginView):
    """View to login the user."""
    template_name = 'twf/users/login.html'
    page_title = 'Login'
    authentication_form = LoginForm


class TWFHomePasswordChangeView(TWFHomeView, PasswordChangeView):
    """View to change the password of the user."""
    template_name = 'twf/users/change_password.html'
    page_title = 'Change Password'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('twf:home')


class TWFHomeUserOverView(TWFHomeView):
    """View to display an overview of the user."""
    template_name = 'twf/users/overview.html'
    page_title = 'User Overview'

    def get_context_data(self, **kwargs):
        """Add the user summary to the context."""
        context = super().get_context_data(**kwargs)
        context['summary'] = self.get_user_summary()
        return context

    def get_user_summary(self):
        """Get the summary of the user."""
        # Get the current date and time
        current_time = now()

        # Define the time ranges
        last_day = current_time - timedelta(days=1)
        last_week = current_time - timedelta(weeks=1)
        last_month = current_time - timedelta(days=30)

        models = [Project, Document, Page, Dictionary, DictionaryEntry, PageTag, Variation, DateVariation]

        summary = {
            'created_last_day': 0,
            'edited_last_day': 0,
            'created_last_week': 0,
            'edited_last_week': 0,
            'created_last_month': 0,
            'edited_last_month': 0,
            'created_total': 0,
            'edited_total': 0,
        }

        user_id = self.request.user.id
        for model in models:
            summary['created_last_day'] += model.objects.filter(created_by_id=user_id, created_at__gte=last_day).count()
            summary['edited_last_day'] += model.objects.filter(modified_by_id=user_id,
                                                               modified_at__gte=last_day).count()

            summary['created_last_week'] += model.objects.filter(created_by_id=user_id,
                                                                 created_at__gte=last_week).count()
            summary['edited_last_week'] += model.objects.filter(modified_by_id=user_id,
                                                                modified_at__gte=last_week).count()

            summary['created_last_month'] += model.objects.filter(created_by_id=user_id,
                                                                  created_at__gte=last_month).count()
            summary['edited_last_month'] += model.objects.filter(modified_by_id=user_id,
                                                                 modified_at__gte=last_month).count()

            summary['created_total'] += model.objects.filter(created_by_id=user_id).count()
            summary['edited_total'] += model.objects.filter(modified_by_id=user_id).count()

        return summary


class TWFHomeUserManagementView(TWFHomeView):
    """View to manage the users."""
    template_name = 'twf/users/management.html'
    page_title = 'User Management'

    def get_context_data(self, **kwargs):
        """Add the user profiles to the context."""
        context = super().get_context_data(**kwargs)
        project_id = self.request.session.get('project_id', None)
        member_profiles = Project.objects.get(pk=project_id).members.all()

        permission_matrix = {}
        for profile in member_profiles:
            user_permission = []
            for group in TWF_GROUPS:
                user_permission.append(profile.user.groups.filter(name=group).exists())
            permission_matrix[profile.user.username] = user_permission

        context['member_profiles'] = permission_matrix
        context['twf_groups'] = TWF_GROUPS
        return context


