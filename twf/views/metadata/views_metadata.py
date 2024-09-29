import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from twf.forms.dynamic_forms import DynamicForm
from twf.forms.metadata_forms import LoadMetadataForm, ExtractMetadataValuesForm, LoadSheetsMetadataForm
from twf.models import Page, Document, PageTag
from twf.views.views_base import TWFView


class TWFMetadataView(LoginRequiredMixin, TWFView):
    """Base view for all project views."""
    template_name = 'twf/metadata/overview.html'
    page_title = 'Metadata Overview'

    def get_context_data(self, **kwargs):
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
                    {'url': reverse('twf:metadata_load_metadata'), 'value': 'Load JSON Metadata'},
                    {'url': reverse('twf:metadata_load_sheets_metadata'), 'value': 'Load Google Sheets Metadata'},
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

    def get_navigation_index(self):
        return 4


class TWFMetadataOverviewView(TWFMetadataView):
    """View for the metadata overview."""
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
    """View for loading metadata from a JSON file."""
    template_name = 'twf/metadata/load_data.html'
    page_title = 'Load Metadata'
    form_class = LoadMetadataForm
    success_url = reverse_lazy('twf:metadata_load_metadata')

    def form_valid(self, form):
        form.is_valid()

        # Get the project
        project = self.get_project()

        # Get form data
        data_target_type = form.cleaned_data['data_target_type']
        json_data_key = form.cleaned_data['json_data_key']
        data_file = form.cleaned_data['data_file']
        match_to_field = form.cleaned_data['match_to_field']
        print("Debug", data_target_type, json_data_key, data_file, match_to_field)

        # Open uploaded file and read the content as json
        data = data_file.read()
        data = json.loads(data)

        # Iterate over the data and save the metadata
        for item in data:
            id_value_of_item = item[json_data_key]

            if data_target_type == 'document':
                try:
                    document = None
                    if match_to_field == 'dbid':
                        document = Document.objects.get(project=project, id=id_value_of_item)
                    elif match_to_field == 'docid':
                        document = Document.objects.get(project=project, document_id=id_value_of_item)
                        print("Found document", document)
                    if document:
                        document.metadata['import'] = item
                        document.save(current_user=self.request.user)
                        print("Saved document", document)

                except Document.DoesNotExist:
                    print(f"Document with {match_to_field} {id_value_of_item} does not exist.")

            elif data_target_type == 'page':
                try:
                    page = None
                    if match_to_field == 'dbid':
                        page = Page.objects.get(document__project=project, id=id_value_of_item)
                    elif match_to_field == 'docid':
                        page = Page.objects.get(document__project=project, dbid=id_value_of_item)
                    if page:
                        page.metadata['import'] = item
                        page.save(current_user=self.request.user)
                except Page.DoesNotExist:
                    print(f"Page with {match_to_field} {id_value_of_item} does not exist.")

        return super().form_valid(form)


class TWFMetadataLoadSheetsDataView(FormView, TWFMetadataView):
    """View for loading metadata from Google Sheets."""
    template_name = 'twf/metadata/load_sheets_data.html'
    page_title = 'Load Google Sheets Metadata'
    form_class = LoadSheetsMetadataForm
    success_url = reverse_lazy('twf:metadata_load_metadata')

    def form_valid(self, form):
        super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()
        return kwargs


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
    """View for reviewing page metadata."""
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
