from statistics import median

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import connection
from django.db.models import Count, Avg, Q
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from twf.forms.dynamic_forms import DynamicForm
from twf.forms.project_forms import QueryDatabaseForm, GeneralSettingsForm, CredentialsForm, \
    TaskSettingsForm, ExportSettingsForm
from twf.models import Project, Document, Page, PageTag
from twf.project_statistics import get_document_statistics
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
                ]
            },
            {
                'name': 'Setup Project',
                'options': [
                    {'url': reverse('twf:project_tk_export'), 'value': 'Request Transkribus Export'},
                    {'url': reverse('twf:project_tk_structure'), 'value': 'Extract Transkribus Export'},
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
        return 1

    def get_context_data(self, **kwargs):
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
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.get_project().tasks.all()
        return context


class TWFProjectPromptsView(TWFProjectView):
    """View for the project task monitor."""
    template_name = 'twf/project/prompts.html'
    page_title = 'Prompts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prompts'] = self.get_project().prompts.all()
        return context


class TWFProjectGeneralSettingsView(FormView, TWFProjectView):
    """View for the general project settings."""
    template_name = 'twf/project/settings/settings_general.html'
    page_title = 'General Project Settings'
    form_class = GeneralSettingsForm
    success_url = reverse_lazy('twf:project_settings_general')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_project()
        return kwargs

    def form_valid(self, form):
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
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        # Save the form
        self.object = form.save(commit=False)
        self.object.save(current_user=self.request.user)

        # Add a success message
        messages.success(self.request, 'Project Credential settings have been updated successfully.')
        # Redirect to the success URL
        return super().form_valid(form)


class TWFProjectTaskSettingsView(FormView, TWFProjectView):
    """View for the project task settings."""
    template_name = 'twf/project/settings/settings_tasks.html'
    page_title = 'Tasks Project Settings'
    form_class = TaskSettingsForm
    success_url = reverse_lazy('twf:project_settings_tasks')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        # Save the form
        self.object = form.save(commit=False)
        self.object.save(current_user=self.request.user)

        # Add a success message
        messages.success(self.request, 'Project Task settings have been updated successfully.')
        # Redirect to the success URL
        return super().form_valid(form)


class TWFProjectExportSettingsView(FormView, TWFProjectView):
    """View for the project task settings."""
    template_name = 'twf/project/settings/settings_export.html'
    page_title = 'Export Project Settings'
    form_class = ExportSettingsForm
    success_url = reverse_lazy('twf:project_settings_tasks')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        # Save the form
        self.object = form.save(commit=False)
        self.object.save(current_user=self.request.user)

        # Add a success message
        messages.success(self.request, 'Project Task settings have been updated successfully.')
        # Redirect to the success URL
        return super().form_valid(form)


class TWFProjectQueryView(FormView, TWFProjectView):
    """View for querying the database."""
    template_name = 'twf/project/query.html'
    page_title = 'SQL Query'
    form_class = QueryDatabaseForm
    results = None

    def form_valid(self, form):
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
        context = super().get_context_data(**kwargs)
        context['results'] = self.results
        return context


class TWFProjectOverviewView(TWFProjectView):
    """View for the project overview."""
    template_name = 'twf/project/overview.html'
    page_title = 'Project Overview'

    def get_context_data(self, **kwargs):
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


def select_project(request, pk):
    request.session['project_id'] = pk
    return redirect('twf:project_overview')


"""def cut_collection_item(request, pk, anno_idx):
    collection_item = CollectionItem.objects.get(pk=pk)
    annotations = collection_item.document_configuration['annotations']

    first_part = annotations[:anno_idx-1]
    second_part = annotations[anno_idx:]

    collection_item.document_configuration['annotations'] = first_part

    collection_item_copy = copy.deepcopy(collection_item)
    collection_item_copy.pk = None
    collection_item_copy.document_configuration['annotations'] = second_part

    collection_item_copy.save(current_user=request.user)
    collection_item.save(current_user=request.user)

    previous_url = request.META.get('HTTP_REFERER')
    if previous_url:
        return redirect(previous_url)
    else:
        return redirect('twf:project_collections')


def mark_collection_item_as_done(request, pk):
    collection_item = CollectionItem.objects.get(pk=pk)
    collection_item.marked_as_done = True
    collection_item.save(current_user=request.user)

    previous_url = request.META.get('HTTP_REFERER')
    if previous_url:
        return redirect(previous_url)
    else:
        return redirect('twf:project_collections')


def mark_collection_item_as_faulty(request, pk):
    collection_item = CollectionItem.objects.get(pk=pk)
    collection_item.marked_as_faulty = True
    collection_item.save(current_user=request.user)

    previous_url = request.META.get('HTTP_REFERER')
    if previous_url:
        return redirect(previous_url)
    else:
        return redirect('twf:project_collections')


from django.shortcuts import render"""


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
