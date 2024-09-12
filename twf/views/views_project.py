import copy
from statistics import median

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db import connection
from django.db.models import Count, Avg, Q
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from twf.filters import DocumentFilter
from twf.forms.dynamic_forms import DynamicForm
from twf.forms.project_forms import ProjectForm, QueryDatabaseForm, DocumentForm
from twf.models import Project, Document, TWF_GROUPS, Page, PageTag
from twf.tables.tables import DocumentTable
from twf.views.views_base import TWFHomeView, TWFView


class TWFProjectView(LoginRequiredMixin, TWFView):
    """Base view for all project views."""
    template_name = 'twf/project/overview.html'

    def get_sub_navigation(self):
        """Get the sub navigation."""
        sub_nav = [
            {
                'name': 'Project Data',
                'options': [
                    {'url': reverse('twf:project_overview'), 'value': 'Overview'},
                    {'url': reverse('twf:project_setup'), 'value': 'Setup', 'active_on': [
                        reverse('twf:project_tk_export'),
                        reverse('twf:project_tk_structure'),
                        reverse('twf:project_sheets_metadata')
                    ]},
                    {'url': reverse('twf:project_documents'), 'value': 'Documents'},
                    {'url': reverse('twf:project_settings'), 'value': 'Settings'},
                ]
            },
            {
                'name': 'Project Options',
                'options': [
                    {'url': reverse('twf:project_query'), 'value': 'Query'},
                    {'url': reverse('twf:project_ai_query'), 'value': 'Ask ChatGPT'},
                ]
            },
            {
                'name': 'Export Data',
                'options': [
                    {'url': reverse('twf:project_export_documents'), 'value': 'Export Documents'},
                    {'url': reverse('twf:project_export_collections'), 'value': 'Export Collections'},
                    {'url': reverse('twf:project_export_project'), 'value': 'Export project'},
                ]
            },
            {
                'name': 'Project Batch',
                'options': [
                    {'url': reverse('twf:project_batch_openai'), 'value': 'Open AI'},
                ]
            },
        ]
        return sub_nav

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if len(context['navigation']['items']) > 1:
            context['navigation']['items'][1]['active'] = True
        return context

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.page_title is None:
            self.page_title = kwargs.get('page_title', 'Project View')


class TWFProjectDocumentsView(SingleTableView, FilterView, TWFProjectView):
    """View for displaying project documents."""
    template_name = 'twf/project/documents.html'
    page_title = 'Project Documents'
    table_class = DocumentTable
    filterset_class = DocumentFilter
    paginate_by = 10
    model = Document

    def get_queryset(self):
        queryset = Document.objects.filter(project_id=self.request.session.get('project_id'))
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['filter'] = self.get_filterset(self.filterset_class)
        context['context_sub_nav'] = self.get_sub_pages()
        return context

    @staticmethod
    def get_sub_pages():
        return {"options": [
            {"url": reverse('twf:project_documents'), "value": "Overview"},
            {"url": reverse('twf:create_document'), "value": "Manually Create Document"},
            {"url": reverse('twf:name_documents'), "value": "Name Documents"},
            {"url": reverse('twf:project_setup'),
             "value": mark_safe('<i class="fa-solid fa-arrow-right-from-bracket"></i> Import Documents')},
            {"url": reverse('twf:metadata_load_metadata'),
             "value": mark_safe('<i class="fa-solid fa-arrow-right-from-bracket"></i> Load Metadata')},
        ]}


class TWFProjectDocumentView(TWFProjectView):
    template_name = 'twf/project/document.html'
    page_title = 'Document'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.request.session.get('project_id')
        if project_id:
            context['document'] = Document.objects.get(pk=self.kwargs.get('pk'))
        return context


class TWFProjectDocumentCreateView(FormView, TWFProjectView):
    template_name = 'twf/project/create_document.html'
    page_title = 'Create Document'
    form_class = DocumentForm
    success_url = reverse_lazy('twf:project_documents')
    object = None

    def form_valid(self, form):
        # Save the form
        self.object = form.save(commit=False)
        self.object.project_id = self.request.session.get('project_id')
        self.object.save(current_user=self.request.user)

        # Add a success message
        messages.success(self.request, 'Document has been created successfully.')
        # Redirect to the success URL
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.request.session.get('project_id')
        context['context_sub_nav'] = TWFProjectDocumentsView.get_sub_pages()
        return context


class TWFProjectDocumentNameView(TWFProjectView):
    template_name = 'twf/project/name_documents.html'
    page_title = 'Name Documents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.request.session.get('project_id')
        context['context_sub_nav'] = TWFProjectDocumentsView.get_sub_pages()
        return context


class TWFProjectSettingsView(FormView, TWFProjectView):
    template_name = 'twf/project/settings.html'
    page_title = 'Project Settings'
    form_class = ProjectForm
    success_url = reverse_lazy('twf:project_settings')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        project_id = self.request.session.get('project_id')
        if project_id:
            kwargs['instance'] = Project.objects.get(pk=project_id)
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


class TWFProjectSetupView(TWFProjectView):
    template_name = 'twf/project/setup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['context_sub_nav'] = {"options": [
            {"url": reverse('twf:project_setup'), "value": "Setup Overview"},
            {"url": reverse('twf:project_tk_export'), "value": "Request Transkribus Export"},
            {"url": reverse('twf:project_tk_structure'), "value": "Extract Transkribus Data"},
            {"url": reverse('twf:project_tk_structure'), "value": "Import Data From JSON File"},
            {"url": reverse('twf:project_sheets_metadata'), "value": "Sheets Metadata"},
        ]}
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


class TWFProjectQueryView(FormView, TWFProjectView):
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
    template_name = 'twf/project/overview.html'
    page_title = 'Project Overview'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_project()
        document_count = Document.objects.filter(project=project).count()
        page_count = Page.objects.filter(document__project=project).count()
        ignored_pages = Page.objects.filter(document__project=project, is_ignored=True).count()
        ignored_percentage = (ignored_pages / page_count * 100) if page_count > 0 else 0
        largest_document = (Document.objects.annotate(num_pages=Count('pages'))
                            .filter(project=project).order_by('-num_pages').first())
        smallest_document = (Document.objects.annotate(num_pages=Count('pages'))
                             .filter(project=project).order_by('num_pages').first())
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
            'document_count': document_count,
            'page_count': page_count,
            'ignored_pages': ignored_pages,
            'ignored_percentage': ignored_percentage,
            'largest_document': largest_document,
            'smallest_document': smallest_document,
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
    # Example JSON data

    json_data = Page.objects.get(pk=pk).metadata

    if request.method == "POST":
        form = DynamicForm(request.POST, json_data=json_data)
        if form.is_valid():
            # Process the data in form.cleaned_data
            pass
    else:
        form = DynamicForm(json_data=json_data)

    return render(request, 'twf/project/document_metadata.html', {'form': form})
