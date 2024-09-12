from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from twf.forms.dynamic_forms import DynamicForm
from twf.forms.metadata_forms import LoadMetadataForm, ExtractMetadataValuesForm
from twf.models import Page, Document, PageTag
from twf.views.views_base import TWFView


class TWFMetadataView(LoginRequiredMixin, TWFView):
    """Base view for all project views."""
    template_name = 'twf/metadata/overview.html'
    page_title = 'Tags Overview'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['navigation']['items'][3]['active'] = True
        return context

    def get_sub_navigation(self):
        """Get the sub navigation."""
        sub_nav = [
            {
                'name': 'Metadata Overview',
                'options': [
                    {'url': reverse('twf:metadata_overview'), 'value': 'Overview'},
                ]
            },
            {
                'name': 'Load Metadata',
                'options': [
                    {'url': reverse('twf:metadata_load_metadata'), 'value': 'Load JSON Metadata'},
                    {'url': reverse('twf:metadata_load_metadata'), 'value': 'Load Google Sheets Metadata'},
                ]
            },
            {
                'name': 'Metadata Workflows',
                'options': [
                    {'url': reverse('twf:metadata_extract'), 'value': 'Extract Controlled Values'},
                    {'url': reverse('twf:metadata_review_documents'), 'value': 'Review Document Metadata'},
                    {'url': reverse('twf:metadata_review_pages'), 'value': 'Review Page Metadata'},
                ]
            }
        ]
        return sub_nav


class TWFMetadataOverviewView(TWFMetadataView):
    template_name = 'twf/metadata/overview.html'
    page_title = 'Metadata Overview'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()

        documents = Document.objects.filter(project=project)
        documents_with_metadata_count = documents.exclude(metadata={}).count()

        pages = Page.objects.filter(document__project=project)
        pages_with_metadata_count = pages.exclude(metadata={}).count()

        context['doc_count'] = documents_with_metadata_count
        context['doc_total_count'] = documents.count()

        context['page_count'] = pages_with_metadata_count
        context['page_total_count'] = pages.count()


        return context


class TWFMetadataLoadDataView(FormView, TWFMetadataView):
    template_name = 'twf/metadata/load_data.html'
    page_title = 'Load Metadata'
    form_class = LoadMetadataForm
    success_url = reverse_lazy('twf:metadata_load_metadata')


class TWFMetadataExtractTagsView(FormView, TWFMetadataView):
    template_name = 'twf/metadata/extract.html'
    page_title = 'Extract Metadata Values'
    form_class = ExtractMetadataValuesForm
    success_url = reverse_lazy('twf:metadata_extract')

    def form_valid(self, form):
        # Save the metadata
        form.is_valid()

        # Get the project
        project = self.get_project()

        # Get the json data key
        json_data_key = form.cleaned_data['json_data_key']

        # Get the dictionary
        dictionary = form.cleaned_data['dictionary']

        data = Page.objects.filter(document__project=project)

        # Loop through the data
        for item in data:
            # Get the metadata
            metadata = item.metadata
            page_tags = item.tags.filter(variation_type=json_data_key)
            page_tags.delete()

            # Check if the json data key exists
            if json_data_key in metadata:
                # Get the value
                value = metadata[json_data_key]
                if value and not value.strip() == '':
                    new_tag = PageTag(
                        page=item,
                        variation_type=json_data_key,
                        variation=value,
                    )
                    new_tag.save(current_user=self.request.user)

        return super().form_valid(form)

    def get_example_keys(self):
        return ['dbid', 'docid', 'title', 'author', 'date', 'language', 'genre', 'keywords', 'notes']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['found_key'] = self.get_example_keys()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs


class TWFMetadataReviewPagesView(FormView, TWFMetadataView):
    template_name = 'twf/metadata/review_page.html'
    page_title = 'Review Page Metadata'
    form_class = DynamicForm
    success_url = reverse_lazy('twf:metadata_review_pages')

    def get_next_page(self):
        try:
            next_page = Page.objects.filter(document__project=self.get_project()).exclude(metadata={}).order_by('modified_at').first()
        except Page.DoesNotExist:
            next_page = None
        return next_page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = self.get_next_page()
        return context

    def get_form_kwargs(self):
        metadata = {}
        next_page = self.get_next_page()
        if next_page:
            metadata = next_page.metadata

        kwargs = super().get_form_kwargs()
        kwargs['json_config'] = self.get_project().page_metadata_fields
        kwargs['json_data'] = metadata
        return kwargs

    def form_valid(self, form):
        # Save the metadata
        form.is_valid()
        config = self.get_project().page_metadata_fields
        print("BLA", form.cleaned_data)
        next_page = self.get_next_page()
        next_page.save(current_user=self.request.user)
        # print(next_page.metadata['name'])
        return super().form_valid(form)


class TWFMetadataReviewDocumentsView(FormView, TWFMetadataView):
    template_name = 'twf/metadata/review_document.html'
    page_title = 'Review Document Metadata'
    form_class = DynamicForm
    success_url = reverse_lazy('twf:metadata_review_documents')

    def get_next_document(self):
        try:
            next_page = Document.objects.filter(project=self.get_project()).exclude(metadata={}).order_by('modified_at').first()
        except Document.DoesNotExist:
            next_page = None
        return next_page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document'] = self.get_next_document()
        return context

    def get_form_kwargs(self):
        metadata = {}
        next_page = self.get_next_document()
        if next_page:
            metadata = next_page.metadata

        kwargs = super().get_form_kwargs()
        kwargs['json_config'] = self.get_project().document_metadata_fields
        kwargs['json_data'] = metadata
        return kwargs

    def form_valid(self, form):
        # Save the metadata
        form.is_valid()
        print("BLA", form.cleaned_data)
        return super().form_valid(form)