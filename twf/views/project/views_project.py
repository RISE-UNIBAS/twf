"""Views for the project section."""
from datetime import timedelta
from statistics import median

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.db.models import Count, Avg, Q
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import FormView

from twf.forms.dynamic_forms import DynamicForm
from twf.forms.project_forms import QueryDatabaseForm, GeneralSettingsForm, CredentialsForm, \
    TaskSettingsForm, ExportSettingsForm, TaskFilterForm, PromptFilterForm
from twf.models import Document, Page, PageTag, Project
from twf.permissions import check_permission, get_actions_grouped_by_category, get_available_actions
from twf.utils.project_statistics import get_document_statistics
from twf.views.views_base import TWFView


class TWFProjectView(LoginRequiredMixin, TWFView):
    """Base view for all project views."""
    template_name = None

    def get_sub_navigation(self):
        """Get the sub navigation."""
        sub_nav = [
            {
                'name': 'Project',
                'options': [
                    {'url': reverse('twf:project_overview'), 'value': 'Overview'},
                    {'url': reverse('twf:project_task_monitor'), 'value': 'Task Monitor'},
                    {'url': reverse('twf:project_prompts'), 'value': 'Saved Prompts'},
                ]
            },
            {
                'name': 'Settings',
                'options': [
                    {'url': reverse('twf:project_settings_general'), 'value': 'General Settings'},
                    {'url': reverse('twf:project_settings_credentials'), 'value': 'Credential Settings'},
                    {'url': reverse('twf:project_settings_tasks'), 'value': 'Task Settings'},
                    {'url': reverse('twf:project_settings_export'), 'value': 'Export Settings'},
                    {'url': reverse('twf:user_management'), 'value': 'User Management'},
                ]
            },
            {
                'name': 'Setup Project',
                'options': [
                    {'url': reverse('twf:project_tk_export'), 'value': 'Request Transkribus Export'},
                    {'url': reverse('twf:project_test_export'), 'value': 'Test Export'},
                    {'url': reverse('twf:project_tk_structure'), 'value': 'Extract Transkribus Export'},
                    {'url': reverse('twf:project_copy'), 'value': 'Create Copy of Project'},
                    {'url': reverse('twf:project_reset'), 'value': 'Reset Functions'},
                ]
            },
            {
                'name': 'Ask Questions',
                'options': [
                    {'url': reverse('twf:project_query'), 'value': 'Query'},
                    {'url': reverse('twf:project_ai_query'), 'value': 'Ask ChatGPT'},
                ]
            },
        ]
        return sub_nav

    def get_navigation_index(self):
        """Get the index of the navigation."""
        return 1

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        return context

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.page_title is None:
            self.page_title = kwargs.get('page_title', 'Project View')


class TWFProjectTaskMonitorView(TWFProjectView):
    """View for the project task monitor."""

    template_name = 'twf/project/task_monitor.html'
    page_title = 'Task Monitor'

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        tasks = self.get_project().tasks.all()

        # Handle filtering
        filter_form = TaskFilterForm(self.request.GET or None)
        if filter_form.is_valid():
            if filter_form.cleaned_data['started_by']:
                tasks = tasks.filter(user=filter_form.cleaned_data['started_by'])
            if filter_form.cleaned_data['status']:
                tasks = tasks.filter(status=filter_form.cleaned_data['status'])

            # Date range filter
            date_range = filter_form.cleaned_data['date_range']
            if date_range == "last_week":
                tasks = tasks.filter(start_time__gte=now() - timedelta(days=7))
            elif date_range == "last_month":
                tasks = tasks.filter(start_time__gte=now() - timedelta(days=30))
            elif date_range == "last_year":
                tasks = tasks.filter(start_time__gte=now() - timedelta(days=365))

        context['tasks'] = tasks
        context['filter_form'] = filter_form
        return context



class TWFProjectPromptsView(TWFProjectView):
    """View for the project prompts."""

    template_name = 'twf/project/prompts.html'
    page_title = 'Prompts'

    def get_context_data(self, **kwargs):
        """Get the context data."""

        context = super().get_context_data(**kwargs)
        prompts = self.get_project().prompts.all()

        # Handle filtering
        filter_form = PromptFilterForm(self.request.GET or None)
        if filter_form.is_valid():
            if filter_form.cleaned_data['system_role']:
                prompts = prompts.filter(system_role__icontains=filter_form.cleaned_data['system_role'])
            if filter_form.cleaned_data['has_document_context'] == "yes":
                prompts = prompts.filter(document_context__isnull=False)
            elif filter_form.cleaned_data['has_document_context'] == "no":
                prompts = prompts.filter(document_context__isnull=True)
            if filter_form.cleaned_data['has_page_context'] == "yes":
                prompts = prompts.filter(page_context__isnull=False)
            elif filter_form.cleaned_data['has_page_context'] == "no":
                prompts = prompts.filter(page_context__isnull=True)
            if filter_form.cleaned_data['has_collection_context'] == "yes":
                prompts = prompts.filter(collection_context__isnull=False)
            elif filter_form.cleaned_data['has_collection_context'] == "no":
                prompts = prompts.filter(collection_context__isnull=True)

        context['prompts'] = prompts
        context['filter_form'] = filter_form
        return context



class TWFProjectGeneralSettingsView(FormView, TWFProjectView):
    """View for the general project settings."""

    template_name = 'twf/project/settings/settings_general.html'
    page_title = 'General Project Settings'
    form_class = GeneralSettingsForm
    success_url = reverse_lazy('twf:project_settings_general')

    def get_form_kwargs(self):
        """Get the form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        """Handle the form submission."""
        # Save the form
        self.object = form.save(commit=False)
        self.object.save(current_user=self.request.user)
        form.save_m2m()

        # Add a success message
        messages.success(self.request, 'Project settings have been updated successfully.')
        # Redirect to the success URL
        return super().form_valid(form)


class TWFProjectCredentialsSettingsView(FormView, TWFProjectView):
    """View for the general project settings."""

    template_name = 'twf/project/settings/settings_credentials.html'
    page_title = 'Credentials Project Settings'
    form_class = CredentialsForm
    success_url = reverse_lazy('twf:project_settings_credentials')

    def get_form_kwargs(self):
        """Get the form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        """Handle the form submission."""
        # Save the form and show a success message
        self.object = form.save(commit=False)
        self.object.save(current_user=self.request.user)
        messages.success(self.request, 'Project Credential settings have been updated successfully.')

        # Retrieve the active tab from form data and include it in the success URL
        active_tab = form.cleaned_data.get('active_tab', 'transkribus')
        success_url = f"{self.success_url}?tab={active_tab}"

        return HttpResponseRedirect(success_url)


class TWFProjectTaskSettingsView(FormView, TWFProjectView):
    """View for the project task settings."""

    template_name = 'twf/project/settings/settings_tasks.html'
    page_title = 'Tasks Project Settings'
    form_class = TaskSettingsForm
    success_url = reverse_lazy('twf:project_settings_tasks')

    def get_form_kwargs(self):
        """Get the form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        """Handle the form submission."""
        # Save the form and show a success message
        self.object = form.save(commit=False)
        self.object.save(current_user=self.request.user)
        messages.success(self.request, 'Project Credential settings have been updated successfully.')

        # Retrieve the active tab from form data and include it in the success URL
        active_tab = form.cleaned_data.get('active_tab', 'transkribus')
        success_url = f"{self.success_url}?tab={active_tab}"

        return HttpResponseRedirect(success_url)


class TWFProjectExportSettingsView(FormView, TWFProjectView):
    """View for the project task settings."""

    template_name = 'twf/project/settings/settings_export.html'
    page_title = 'Export Project Settings'
    form_class = ExportSettingsForm
    success_url = reverse_lazy('twf:project_settings_export')

    def get_form_kwargs(self):
        """Get the form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        """Handle the form submission."""
        # Save the form
        self.object = form.save(commit=False)
        self.object.save(current_user=self.request.user)

        # Add a success message
        messages.success(self.request, 'Project Task settings have been updated successfully.')
        # Redirect to the success URL
        return super().form_valid(form)


class TWFProjectQueryView(FormView, TWFProjectView):
    """View for querying the database."""

    template_name = 'twf/project/query/query.html'
    page_title = 'SQL Query'
    form_class = QueryDatabaseForm
    results = None

    def form_valid(self, form):
        """Handle the form submission."""
        sql_query = form.cleaned_data['query']
        print(sql_query)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                columns = [col[0] for col in cursor.description]
                print(columns)
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                if len(results) == 0:
                    messages.info(self.request, 'No results found.')

                self.results = results
        except Exception as e:
            messages.error(self.request, f'Error executing query: {e}')
            return self.render_to_response(self.get_context_data(form=form))

        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context['results'] = self.results
        return context


class TWFProjectOverviewView(TWFProjectView):
    """View for the project overview."""

    template_name = 'twf/project/overview.html'
    page_title = 'Project Overview'

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)

        project = self.get_project()
        context['doc_stats'] = get_document_statistics(project)

        pagetag_count = PageTag.objects.filter(page__document__project=project).count()

        unique_pagetag_count = (PageTag.objects.filter(page__document__project=project)
        .aggregate(unique_variations=Count('variation', distinct=True))['unique_variations'])
        average_pagetags_per_document = (Document.objects.annotate(num_pagetags=Count('pages__tags'))
        .filter(project=project)
        .aggregate(average_pagetags=Avg('num_pagetags'))['average_pagetags'])
        pagetags_per_document_list = (Document.objects.annotate(num_pagetags=Count('pages__tags'))
                                      .filter(project=project).values_list('num_pagetags', flat=True))
        median_pagetags_per_document = median(pagetags_per_document_list) if pagetags_per_document_list else 0
        total_pagetags = PageTag.objects.filter(page__document__project=project).count()
        pagetags_with_dictionaryentry = PageTag.objects.filter(Q(page__document__project=project) &
                                                               (Q(dictionary_entry__isnull=False) |
                                                                Q(date_variation_entry__isnull=False))).count()
        percentage_with_dictionaryentry = (pagetags_with_dictionaryentry / total_pagetags * 100) \
            if total_pagetags > 0 else 0

        context['stats'] = {
            'pagetag_count': pagetag_count,
            'unique_pagetag_count': unique_pagetag_count,
            'average_pagetags_per_document': average_pagetags_per_document,
            'median_pagetags_per_document': median_pagetags_per_document,
            'total_pagetags': total_pagetags,
            'pagetags_with_dictionaryentry': pagetags_with_dictionaryentry,
            'percentage_with_dictionaryentry': percentage_with_dictionaryentry
        }
        return context


class TWFProjectUserManagementView(TWFProjectView):
    """View to manage the users."""
    template_name = 'twf/project/user_management.html'
    page_title = 'User Management'

    def get_context_data(self, **kwargs):
        """Add the user profiles to the context."""
        context = super().get_context_data(**kwargs)

        project = self.get_project()
        users = [project.owner] + list(project.members.all())
        context['users'] = users
        context['permissions'] = get_actions_grouped_by_category(project, profile=self.request.user.profile)

        return context

    def post(self, request, *args, **kwargs):
        """Handle the post request."""
        project = self.get_project()
        context = self.get_context_data()

        for profile in context['users']:
            for action in get_available_actions(project).keys():
                form_field_name = f"{profile.user.username}__{action}"
                if form_field_name in request.POST:
                    profile.add_permission(action, project)
                else:
                    profile.remove_permission(action, project)
            profile.save()

        messages.success(request, 'Permissions have been updated successfully.')
        return redirect(reverse('twf:user_management'))


class TWFProjectCopyView(TWFProjectView):
    """View for copying a project."""

    template_name = 'twf/project/setup/copy.html'
    page_title = 'Copy Project'

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        return context


class TWFProjectResetView(TWFProjectView):
    """View for copying a project."""

    template_name = 'twf/project/setup/reset.html'
    page_title = 'Reset Project'

    def post(self, request, *args, **kwargs):
        """Handle the post request."""
        action = request.POST.get('action', None)

        if action == "unpark_all_tags":
            parked_tags = PageTag.objects.filter(page__document__project=self.get_project(), is_parked=True)
            num_tags = parked_tags.count()
            parked_tags.update(is_parked=False)
            messages.success(request, f"{num_tags} parked tags have been un-parked.")
        elif action == "remove_all_prompts":
            all_prompts = self.get_project().prompts.all()
            num_prompts = all_prompts.count()
            all_prompts.delete()
            messages.success(request, f"{num_prompts} prompts have been removed.")
        elif action == "remove_all_tasks":
            all_tasks = self.get_project().tasks.all()
            num_tasks = all_tasks.count()
            all_tasks.delete()
            messages.success(request, f"{num_tasks} tasks have been removed.")
        elif action == "remove_all_dictionaries":
            all_dictionaries = self.get_project().selected_dictionaries.all()
            num_dictionaries = all_dictionaries.count()
            self.get_project().selected_dictionaries.clear()
            messages.success(request, f"{num_dictionaries} dictionaries have been removed.")
        elif action == "remove_documents":
            pass
        elif action == "remove_all_tags":
            pass
        elif action == "remove_all_collections":
            pass

        return redirect('twf:project_reset')

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        return context


def select_project(request, pk):
    """Select a project."""
    request.session['project_id'] = pk
    return redirect('twf:project_overview')

def delete_project(request, pk):
    """Delete a project."""


    try:
        project = Project.objects.get(pk=pk)
        if check_permission(request.user, "delete_project", project):
            project.delete()
            messages.success(request, 'Project has been deleted.')
        else:
            messages.error(request, 'You do not have the required permissions to delete this project.')
    except Project.DoesNotExist:
        messages.error(request, 'Project does not exist.')

    return redirect('twf:project_management')

def close_project(request, pk):
    """Close a project."""

    if check_permission(request.user,
                        "close_project",
                        object_id=pk):
        try:
            project = Project.objects.get(pk=pk)
            project.is_closed = True
            project.save(current_user=request.user)
            messages.success(request, 'Project has been closed.')
        except Project.DoesNotExist:
            messages.error(request, 'Project does not exist.')
    else:
        messages.error(request, 'You do not have the required permissions to close this project.')

    return redirect('twf:project_management')

def dynamic_form_view(request, pk):
    """View for displaying a dynamic form."""

    json_data = Page.objects.get(pk=pk).metadata

    if request.method == "POST":
        form = DynamicForm(request.POST, json_data=json_data)
        if form.is_valid():
            # Process the data in form.cleaned_data
            pass
    else:
        form = DynamicForm(json_data=json_data)

    return render(request, 'twf/documents/document_metadata.html', {'form': form})
