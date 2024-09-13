from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now, timedelta
from twf.forms.user_forms import LoginForm, ChangePasswordForm
from twf.models import Project, Document, Page, Dictionary, DictionaryEntry, PageTag, Variation, DateVariation, \
    TWF_GROUPS
from twf.views.views_base import TWFView


class TWFHomeView(TWFView):
    project_required = False

    """Base view for the home view."""
    template_name = 'twf/base/home.html'

    def get_sub_navigation(self):
        """Get the sub navigation."""
        sub_nav = [
            {
                'name': 'TWF',
                'options': [
                    {'url': reverse('twf:home'), 'value': 'Home'},
                    {'url': reverse('twf:about'), 'value': 'About'},
                ]
            }
        ]
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

    def get_navigation_index(self):
        return 0

    def get_context_data(self, **kwargs):
        """Add the active item to the navigation."""
        context = super().get_context_data(**kwargs)
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


class TWFHomeUserOverView(LoginRequiredMixin, TWFHomeView):
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


class TWFHomeUserManagementView(LoginRequiredMixin, TWFHomeView):
    """View to manage the users."""
    template_name = 'twf/users/management.html'
    page_title = 'User Management'

    def get_context_data(self, **kwargs):
        """Add the user profiles to the context."""
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        if project is not None:
            member_profiles = project.members.all()
        else:
            member_profiles = []

        permission_matrix = {}
        for profile in member_profiles:
            user_permission = []
            for group in TWF_GROUPS:
                user_permission.append(profile.user.groups.filter(name=group).exists())
            permission_matrix[profile.user.username] = user_permission

        context['member_profiles'] = permission_matrix
        context['twf_groups'] = TWF_GROUPS
        return context


class TWFSelectProjectView(LoginRequiredMixin, TWFHomeView):
    template_name = 'twf/project/select.html'
    page_title = 'Select Project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        project = Project.objects.get(pk=self.kwargs.get('pk'))
        user_role = 'member'
        if user.is_superuser:
            user_role = 'admin'
        if project.owner == user:
            user_role = 'owner'
        if project.members.filter(pk=user.pk).exists():
            user_role = 'member'

        groups = []
        for group in TWF_GROUPS:
            db_group, created = Group.objects.get_or_create(name=group)
            groups.append((db_group, user.groups.filter(name=group).exists()))

        context.update(
            {
                'project': project,
                'user_role': user_role,
                'groups': groups
            }
        )

        return context