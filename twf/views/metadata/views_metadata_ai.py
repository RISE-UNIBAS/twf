from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.metadata.metadata_forms import LoadSheetsMetadataForm, LoadMetadataForm
from twf.views.metadata.views_metadata import TWFMetadataView


class TWFMetadataLoadSheetsDataView(FormView, TWFMetadataView):
    """View for loading metadata from Google Sheets."""

    template_name = 'twf/metadata/load_sheets_data.html'
    page_title = 'Load Google Sheets Metadata'
    form_class = LoadSheetsMetadataForm
    success_url = reverse_lazy('twf:metadata_load_sheets_metadata')

    def get_form_kwargs(self):
        """Get the form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_metadata_load_sheets')
        kwargs['data-message'] = "Are you sure you want to load the sheets metadata?"

        return kwargs


class TWFMetadataLoadDataView(FormView, TWFMetadataView):
    """View for loading metadata from a JSON file."""

    template_name = 'twf/metadata/load_data.html'
    page_title = 'Load Metadata'
    form_class = LoadMetadataForm
    success_url = reverse_lazy('twf:metadata_load_metadata')

    def get_form_kwargs(self):
        """Get the form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_metadata_load_json')
        kwargs['data-message'] = "Are you sure you want to load the json metadata?"
        return kwargs