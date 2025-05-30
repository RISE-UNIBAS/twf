"""Views for the metadata section of the TWF application."""
import json
import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from twf.forms.dynamic_forms import DynamicForm
from twf.forms.metadata.metadata_forms import ExtractMetadataValuesForm
from twf.models import Page, Document, PageTag, Variation
from twf.views.views_base import TWFView

logger = logging.getLogger(__name__)


class TWFMetadataView(LoginRequiredMixin, TWFView):
    """Base view for all project views."""
    template_name = 'twf/metadata/overview.html'
    page_title = None

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
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
                    {'url': reverse('twf:metadata_load_metadata'),
                     'value': 'Load JSON Metadata', 'permission': 'metadata.manage'},
                    {'url': reverse('twf:metadata_load_sheets_metadata'),
                     'value': 'Load Google Sheets Metadata', 'permission': 'metadata.manage'},
                ]
            },
            {
                'name': 'Metadata Workflows',
                'options': [
                    {'url': reverse('twf:metadata_extract'),
                     'value': 'Extract Controlled Values', 'permission': 'metadata.manage'},
                    {'url': reverse('twf:metadata_review_documents'),
                     'value': 'Review Document Metadata', 'permission': 'metadata.edit'},
                    {'url': reverse('twf:metadata_review_pages'),
                     'value': 'Review Page Metadata', 'permission': 'metadata.edit'},
                ]
            }
        ]
        return sub_nav

    def get_navigation_index(self):
        """Get the navigation index."""
        return 4


class TWFMetadataOverviewView(TWFMetadataView):
    """View for the metadata overview."""
    template_name = 'twf/metadata/overview.html'
    page_title = 'Metadata'
    show_context_help = False

    def get_context_data(self, **kwargs):
        """Get the context data."""
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

        try:
            context['doc_coverage'] = documents_with_metadata_count / documents.count() * 100
        except ZeroDivisionError:
            context['doc_coverage'] = 0

        return context



class TWFMetadataExtractTagsView(FormView, TWFMetadataView):
    """View for extracting metadata values."""

    template_name = 'twf/metadata/extract.html'
    page_title = 'Extract Metadata Values'
    form_class = ExtractMetadataValuesForm
    success_url = reverse_lazy('twf:metadata_extract')

    def form_valid(self, form):
        # Save the metadata
        form.is_valid()

        # Get the project
        project = self.get_project()

        # Get the json data key and the dictionary
        extract_from = 'documents'  # form.cleaned_data['extract_from']
        json_data_key = form.cleaned_data['json_data_key']
        dictionary = form.cleaned_data['dictionary']
        extracted_values = 0

        if extract_from == 'documents':
            data = Document.objects.filter(project=project)
            for doc in data:
                if 'json_import' in doc.metadata:
                    metadata = doc.metadata['json_import']
                    if json_data_key in metadata:
                        page = doc.pages.order_by('tk_page_number').first()

                        if page.tags.filter(variation=metadata[json_data_key]).exists():
                            page.tags.filter(variation=metadata[json_data_key]).delete()

                        tag = PageTag(page=page,
                                      variation=metadata[json_data_key],
                                      variation_type=dictionary.type,
                                      dictionary_entry=None)
                        # Try to assign the tag to its dictionary entry
                        variations = Variation.objects.filter(entry__dictionary=dictionary,
                                                              variation=metadata[json_data_key])
                        if variations.exists():
                            tag.dictionary_entry = variations.first().entry

                        tag.save(current_user=self.request.user)
                        extracted_values += 1
                else:
                    logger.warning("Document %s has no json metadata", document)

        elif extract_from == 'pages':
            data = Page.objects.filter(document__project=project)
            for page in data:
                if 'json_import' in page.metadata:
                    metadata = page.metadata['json_import']
                    if json_data_key in metadata:
                        tag = PageTag(page=page,
                                      variation=metadata[json_data_key],
                                      variation_type=dictionary.type,
                                      dictionary_entry=None)

                        # Try to assign the tag to its dictionary entry
                        variations = Variation.objects.filter(entry__dictionary=dictionary,
                                                              variation=metadata[json_data_key])
                        if variations.exists():
                            tag.dictionary_entry = variations.first().entry

                        tag.save(current_user=self.request.user)
                        extracted_values += 1
                else:
                    logger.warning("Page %s has no json metadata", page)

        else:
            pass

        messages.success(self.request, f"Extracted {extracted_values} values from the metadata.")
        return super().form_valid(form)

    def get_example_keys(self):
        """Get example keys for the metadata."""
        return ['dbid', 'docid', 'title', 'author', 'date', 'language', 'genre', 'keywords', 'notes']

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context['found_key'] = self.get_example_keys()
        return context

    def get_form_kwargs(self):
        """Get the form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs


class TWFMetadataReviewPagesView(FormView, TWFMetadataView):
    """View for reviewing page metadata."""

    template_name = 'twf/metadata/review_page.html'
    page_title = 'Review Page Metadata'
    form_class = DynamicForm
    success_url = reverse_lazy('twf:metadata_review_pages')

    def get_next_page(self):
        """Get the next page to review."""
        try:
            next_page = (Page.objects.filter(document__project=self.get_project()).
                         exclude(metadata={}).order_by('modified_at').first())
        except Page.DoesNotExist:
            next_page = None
        return next_page

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context['page'] = self.get_next_page()
        return context

    def get_form_kwargs(self):
        """Get the form kwargs."""
        metadata = {}
        next_page = self.get_next_page()
        if next_page:
            metadata = next_page.metadata

        kwargs = super().get_form_kwargs()
        kwargs['json_config'] = (self.get_project().get_task_configuration('metadata_review').
                                 get('page_metadata_review', {}))
        kwargs['json_data'] = metadata
        return kwargs

    def form_valid(self, form):
        """Process the form data."""
        # Save the metadata
        form.is_valid()
        config = self.get_project().get_task_configuration('metadata_review').get('page_metadata_review', {})
        logger.debug("Metadata form cleaned data: %s", form.cleaned_data)
        next_page = self.get_next_page()
        next_page.save(current_user=self.request.user)
        return super().form_valid(form)

import logging
def set_nested_value(d, keys, value):
    """Helper function to set a value in a nested dictionary or list using a list of keys."""
    for key in keys[:-1]:
        logging.info(f"Current d: {d}, current key: {key}")
        if key.isdigit():
            key = int(key)
            if isinstance(d, list):
                while len(d) <= key:
                    d.append({})
            else:
                raise ValueError(f"Expected a list at {key}, but found {type(d).__name__}")
            d = d[key]
        else:
            if isinstance(d, dict):
                d = d.setdefault(key, {})
            else:
                raise ValueError(f"Expected a dict at {key}, but found {type(d).__name__}")

    last_key = keys[-1]
    logging.info(f"Final d before setting value: {d}, final key: {last_key}")
    if last_key.isdigit():
        last_key = int(last_key)
        if isinstance(d, list):
            while len(d) <= last_key:
                d.append({})
            d[last_key] = value
        else:
            raise ValueError(f"Expected a list at {last_key}, but found {type(d).__name__}")
    else:
        if isinstance(d, dict):
            d[last_key] = value
        elif isinstance(d, list):
            raise ValueError(
                f"Expected a dict at {last_key}, but found a list. Possibly incorrect key sequence: {keys}")
        else:
            raise ValueError(f"Unexpected type {type(d).__name__} at {last_key}.")


class TWFMetadataReviewDocumentsView(FormView, TWFMetadataView):
    """View for reviewing document metadata."""

    template_name = 'twf/metadata/review_document.html'
    page_title = 'Review Document Metadata'
    form_class = DynamicForm
    success_url = reverse_lazy('twf:metadata_review_documents')

    def get_next_document(self):
        """Get the next document to review."""
        try:
            next_page = (Document.objects.filter(project=self.get_project()).
                         exclude(metadata={}).order_by('modified_at').first())
        except Document.DoesNotExist:
            next_page = None
        return next_page

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context['document'] = self.get_next_document()
        return context

    def get_form_kwargs(self):
        """Get the form kwargs."""
        metadata = {}
        next_page = self.get_next_document()
        if next_page:
            metadata = next_page.metadata

        kwargs = super().get_form_kwargs()
        metadata_review_config = self.get_project().get_task_configuration('metadata_review', return_json=True)

        doc_config = metadata_review_config.get('document_metadata_review', "{}")
        doc_config = json.loads(doc_config)
        kwargs['json_config'] = doc_config
        kwargs['json_data'] = metadata
        return kwargs

    def form_valid(self, form):
        """Process the form data."""
        # Get the cleaned form data
        cleaned_data = form.cleaned_data

        # Retrieve the document to update its metadata
        next_document = self.get_next_document()
        message = None

        if next_document:
            metadata = next_document.metadata  # Get the existing metadata

            if "submit_park" in self.request.POST:
                print("Would park the document")
                next_document.is_parked = True
                next_document.workflow_remarks = cleaned_data['remarks_field']
                message = f"Parked document {next_document}"

            if "submit_save" in self.request.POST:
                # Update the metadata based on the cleaned form data
                for key, value in cleaned_data.items():
                    if key == 'remarks_field':
                        next_document.workflow_remarks = value
                        continue
                    keys = key.split('.')  # Split by dot notation to get the path
                    set_nested_value(metadata, keys, value)

                # Save the updated metadata back to the document
                next_document.metadata = metadata
                message = f"Saved metadata for document {next_document}"

            next_document.save()
            if message:
                messages.success(self.request, message)
            else:
                messages.error(self.request, "No action taken")
        else:
            messages.error(self.request, "No document found to update")

        return super().form_valid(form)
