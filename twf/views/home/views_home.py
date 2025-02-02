"""Views for the home section of the TWF application."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta
from django.views.generic import FormView

from twf.forms.project.project_forms import CreateProjectForm
from twf.forms.user_forms import LoginForm, ChangePasswordForm, UserProfileForm, CreateUserForm
from twf.models import Project, Document, Page, Dictionary, DictionaryEntry, PageTag, Variation, DateVariation, \
    UserProfile, User
from twf.permissions import get_available_actions
from twf.tasks.instant_tasks import save_instant_task_create_project
from twf.utils.mail_utils import send_welcome_email, send_reset_email
from twf.views.views_base import TWFView


class TWFHomeView(TWFView):
    """Base view for the home view."""
    project_required = False

    """Base view for the home view."""
    template_name = 'twf/home/home.html'

    def get_sub_navigation(self):
        """Get the sub navigation for the home pages."""
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
            user_projects = self.request.user.profile.get_projects().order_by('title')
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

        sub_nav.append({
            'name': 'Administrator Options',
            'options': self.get_admin_options()
        })

        return sub_nav

    def get_user_options(self):
        """Get the user options."""
        user = self.request.user

        if user.is_authenticated:
            nav = [
                {'url': reverse('twf:user_overview'), 'value': 'Your Activity'},
                {'url': reverse('twf:user_profile'), 'value': 'User Information'},
                {'url': reverse('twf:user_change_password'), 'value': 'Change Password'},
                {'url': reverse('twf:user_logout'), 'value': 'Logout'},
            ]

            return nav

        return [
            {'url': reverse('twf:login'), 'value': 'Login'},
        ]

    def get_admin_options(self):
        """Get the admin options."""
        user = self.request.user
        nav = []

        if user.is_superuser or user.is_staff:
            nav.append({'url': reverse('twf:project_create'), 'value': 'Create Project'})
            nav.append({'url': reverse('twf:project_management'), 'value': 'Project Management'})
            nav.append({'url': reverse('twf:twf_user_management'), 'value': 'User Management'})
            nav.append({'url': reverse('admin:index'), 'value': 'Admin Interface'})

        return nav

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
    """View to log in the user."""
    template_name = 'twf/home/users/login.html'
    page_title = 'Login'
    authentication_form = LoginForm


class TWFHomePasswordChangeView(TWFHomeView, PasswordChangeView):
    """View to change the password of the user."""
    template_name = 'twf/home/users/change_password.html'
    page_title = 'Change Password'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('twf:home')


class TWFHomeUserProfileView(LoginRequiredMixin, FormView, TWFHomeView):
    """View to display the user profile."""
    template_name = 'twf/home/users/profile.html'
    page_title = 'User Profile'
    form_class = UserProfileForm
    success_url = reverse_lazy('twf:user_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        if not hasattr(user, 'profile'):
            UserProfile.objects.create(user=user)  # Ensures profile existence

        kwargs['instance'] = user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']

        user.profile.orc_id = form.cleaned_data['orcid']
        user.profile.affiliation = form.cleaned_data['affiliation']
        user.profile.save()

        user.save()
        messages.success(self.request, 'User profile updated successfully.')
        return super().form_valid(form)


class TWFHomeUserOverView(LoginRequiredMixin, TWFHomeView):
    """View to display an overview of the user."""
    template_name = 'twf/home/users/overview.html'
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


class TWFSelectProjectView(LoginRequiredMixin, TWFHomeView):
    """View to select a project."""
    template_name = 'twf/home/select_project.html'
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
        if project.members.filter(user_id=user.pk).exists():
            user_role = 'member'

        context.update(
            {
                'project_to_select': project,
                'project': self.get_project(),
                'user_role': user_role
            }
        )

        return context


class TWFCreateProjectView(LoginRequiredMixin, FormView, TWFHomeView):
    """View to create a project."""
    template_name = 'twf/home/create_project.html'
    page_title = 'Create Project'
    form_class = CreateProjectForm
    success_url = reverse_lazy('twf:home')

    def form_valid(self, form):
        """Save the project and add the user as the owner. Add the selected members to the project.
        Add default permissions to the project owner and members.
        """
        project = form.save(commit=False)
        project.save(current_user=self.request.user)
        members = form.cleaned_data['members']

        member_permissions = get_available_actions(for_group='user')
        for member in members:
            project.members.add(member)
            for perm in member_permissions.keys():
                member.add_permission(perm, project)
            member.save()

        all_permissions = get_available_actions()
        for perm in all_permissions.keys():
            project.owner.add_permission(perm, project)
        project.owner.save()

        save_instant_task_create_project(project, self.request.user)

        messages.success(self.request, 'Project created successfully.')
        return redirect(reverse('twf:project_do_select', args=[project.id]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TWFManageProjectsView(LoginRequiredMixin, TWFHomeView):
    """View to manage the projects."""
    template_name = 'twf/home/manage_projects.html'
    page_title = 'Project Management'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['projects'] = Project.objects.all()
        return context


class TWFManageUsersView(LoginRequiredMixin, FormView, TWFHomeView):
    """View to manage the projects."""
    template_name = 'twf/home/manage_users.html'
    page_title = 'User Management'
    form_class = CreateUserForm
    success_url = reverse_lazy('twf:twf_user_management')

    def post(self, request, *args, **kwargs):
        if 'existing_user_id' in request.POST:
            user = User.objects.get(pk=request.POST.get('existing_user_id'))
            action = request.POST.get('action', None)
            if action == 'user_delete':
                if user == request.user:
                    messages.error(request, 'You cannot delete yourself.')
                    return redirect('twf:twf_user_management')
                user.delete()
                messages.success(request, 'User deleted successfully.')
            elif action == 'pw_reset':
                initial_password = get_random_string(length=8)
                user.set_password(initial_password)
                user.save()
                send_reset_email(user.email, user.username, initial_password)
                messages.success(request, 'Password reset successfully. Message sent to user.')
            elif action == 'user_deactivate':
                user.is_active = False
                user.profile.permissions.clear()
                user.profile.save()
                user.save()
                messages.success(request, 'User deactivated successfully.')
            elif action == 'user_activate':
                user.is_active = True
                user.save()
                messages.success(request, 'User activated successfully.')

            return redirect('twf:twf_user_management')
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        initial_password = get_random_string(length=8)
        user.password = initial_password
        user.save()

        send_welcome_email(user.email, user.username, initial_password)
        messages.success(self.request, 'User created successfully. Message sent to user.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = UserProfile.objects.all().order_by('user__username')
        return context