"""Views for the project section."""
import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now

logger = logging.getLogger(__name__)
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from twf.forms.dynamic_forms import DynamicForm
from twf.forms.filters.filters import TaskFilter, PromptFilter, NoteFilter
from twf.forms.filters.project_filter_forms import TaskFilterForm, PromptFilterForm
from twf.forms.project.project_forms_batches import ProjectCopyBatchForm, DocumentExtractionBatchForm
from twf.forms.project.project_forms import QueryDatabaseForm, GeneralSettingsForm, CredentialsForm, \
    TaskSettingsForm, ExportSettingsForm, RepositorySettingsForm, PromptForm
from twf.models import Page, PageTag, Project, Prompt, Task, Note
from twf.permissions import check_permission, get_actions_grouped_by_category, get_available_actions
from twf.tables.tables_project import TaskTable, PromptTable, NoteTable
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
                    {'url': reverse('twf:project_notes'), 'value': 'Project Notes'},
                ]
            },
            {
                'name': 'Ask Questions',
                'options': [
                    {'url': reverse('twf:project_query'), 'value': 'Query Database'},
                    {'url': reverse('twf:project_ai_query'), 'value': 'Ask ChatGPT'},
                    {'url': reverse('twf:project_gemini_query'), 'value': 'Ask Gemini'},
                    {'url': reverse('twf:project_claude_query'), 'value': 'Ask Claude'},
                    {'url': reverse('twf:project_mistral_query'), 'value': 'Ask Mistral'},
                ]
            },
            {
                'name': 'Settings',
                'options': [
                    {'url': reverse('twf:project_settings_general'),
                     'value': 'General Settings', 'permission': 'change_project_settings'},
                    {'url': reverse('twf:project_settings_credentials'),
                     'value': 'Credential Settings', 'permission': 'change_credential_settings'},
                    {'url': reverse('twf:project_settings_tasks'),
                     'value': 'Task Settings', 'permission': 'change_task_settings'},
                    {'url': reverse('twf:project_settings_export'),
                     'value': 'Export Settings', 'permission': 'change_export_settings'},
                    {'url': reverse('twf:project_settings_repository'),
                     'value': 'Repository Settings', 'permission': 'export_to_zenodo'},
                    {'url': reverse('twf:user_management'),
                     'value': 'User Management', 'permission': 'setup_project_permissions'},
                ]
            },
            {
                'name': 'Setup Project',
                'options': [
                    {'url': reverse('twf:project_tk_export'),
                     'value': 'Request Transkribus Export', 'permission': 'request_transkribus_export'},
                    {'url': reverse('twf:project_test_export'),
                     'value': 'Test Export', 'permission': 'test_transkribus_export'},
                    {'url': reverse('twf:project_tk_structure'),
                     'value': 'Extract Transkribus Export', 'permission': 'extract_transkribus_export'},
                    {'url': reverse('twf:project_copy'),
                     'value': 'Create Copy of Project', 'permission': 'copy_project'},
                    {'url': reverse('twf:project_reset'), 'value': 'Reset Functions'},
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


class TWFProjectTaskMonitorView(SingleTableView, FilterView, TWFProjectView):
    """View for the project task monitor."""

    template_name = 'twf/project/task_monitor.html'
    page_title = 'Task Monitor'
    table_class = TaskTable
    filterset_class = TaskFilter
    paginate_by = 10
    model = Task

    def get_queryset(self):
        """Get the queryset for the view."""
        queryset = Task.objects.filter(project_id=self.request.session.get('project_id'))
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get(self, request, *args, **kwargs):
        """Get the view."""
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        tasks = self.get_project().tasks.all()

        # Handle filtering
        filter_form = TaskFilterForm(self.request.GET or None, project=self.get_project())
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
        context['filter'] = self.get_filterset(self.filterset_class)
        return context


class TWFProjectTaskDetailView(TWFProjectView):
    """View for displaying task details."""
    
    template_name = 'twf/project/task_detail.html'
    page_title = 'Task Details'
    
    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        
        # Get the task
        task_id = self.kwargs.get('pk')
        task = Task.objects.get(pk=task_id)
        context['task'] = task
        
        # Calculate task duration if both start and end times exist
        if task.start_time and task.end_time:
            duration = task.end_time - task.start_time
            # Format duration as hours:minutes:seconds
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            context['duration'] = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

        # Format task metadata as a list of key/value pairs for display
        if task.meta:
            context['meta_items'] = [
                {'key': key, 'value': value} 
                for key, value in task.meta.items() 
                if key not in ['current', 'total', 'text']  # Skip progress-related keys
            ]
        
        return context


class TWFProjectPromptsView(SingleTableView, FilterView, TWFProjectView):
    """View for the project prompts."""

    template_name = 'twf/project/prompts.html'
    page_title = 'Prompts'
    table_class = PromptTable
    filterset_class = PromptFilter
    paginate_by = 10
    model = Prompt

    def get_queryset(self):
        """Get the queryset for the view."""
        queryset = Prompt.objects.filter(project_id=self.request.session.get('project_id'))
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get(self, request, *args, **kwargs):
        """Get the view."""
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context['filter'] = self.get_filterset(self.filterset_class)
        return context


class TWFProjectNotesView(SingleTableView, FilterView, TWFProjectView):
    """View for the project prompts."""

    template_name = 'twf/project/notes.html'
    page_title = 'Notes'
    table_class = NoteTable
    filterset_class = NoteFilter
    paginate_by = 10
    model = Note

    def get_queryset(self):
        """Get the queryset for the view."""
        queryset = Note.objects.filter(project_id=self.request.session.get('project_id'))
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get(self, request, *args, **kwargs):
        """Get the view."""
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context['filter'] = self.get_filterset(self.filterset_class)
        return context

class TWFProjectPromptEditView(FormView, TWFProjectView):
    """View for the project prompts."""

    template_name = 'twf/project/edit_prompt.html'
    page_title = 'Prompts'
    form_class = PromptForm
    success_url = reverse_lazy('twf:project_prompts')

    def get_form_kwargs(self):
        """Get the form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = Prompt.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        """Handle the form submission."""
        # Save the form and show a success message
        self.object = form.save(commit=False)
        self.object.save(current_user=self.request.user)

        messages.success(self.request, 'Prompt has been updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
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


class TWFProjectRepositorySettingsView(FormView, TWFProjectView):
    """View for the project repository settings."""

    template_name = 'twf/project/settings/settings_repository.html'
    page_title = 'Project Repository Settings'
    form_class = RepositorySettingsForm
    success_url = reverse_lazy('twf:project_settings_repository')

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
        messages.success(self.request, 'Project Repository settings have been updated successfully.')
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
        logger.debug("Executing SQL query: %s", sql_query)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                columns = [col[0] for col in cursor.description]
                logger.debug("Query columns: %s", columns)
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
    page_title = 'Project'

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)

        project = self.get_project()
        context['doc_stats'] = get_document_statistics(project)

        transkribus_creds = self.get_project().get_credentials('transkribus')
        username = None
        password = None
        if transkribus_creds:
            username = transkribus_creds['username']
            password = transkribus_creds['password']

        context['steps'] = {
            'transkribus_credentials': username is not None and password is not None,
            'transkribus_export_present': project.downloaded_zip_file and bool(project.downloaded_zip_file.name.strip()),
            'transkribus_export_extracted': project.documents.all().count() > 0,
            'transkribus_tags_extracted': PageTag.objects.filter(page__document__project=project).count() > 0,
            'dictionaries_connected': project.selected_dictionaries.all().count() > 0,
        }

        all_are_true = all(context['steps'].values())
        context['steps']['all_steps_complete'] = all_are_true

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


class TWFProjectCopyView(FormView, TWFProjectView):
    """View for copying a project."""

    template_name = 'twf/project/setup/copy.html'
    page_title = 'Copy Project'
    form_class = ProjectCopyBatchForm
    success_url = reverse_lazy('twf:project_copy')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_project_copy')
        kwargs['data-message'] = "Are you sure you want to copy this project?"

        return kwargs

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
    page_title = 'Extract Transkribus Export'
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