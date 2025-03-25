""" This module contains forms for exporting data from the application. """
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Column, Div, Row
from django import forms
from django_select2.forms import Select2Widget

from twf.clients.zenodo_client import get_zenodo_uploads
from twf.forms.base_batch_forms import BaseBatchForm


class ExportDocumentsForm(BaseBatchForm):

    export_type = forms.ChoiceField(choices=[('documents', 'Documents'), ('pages', 'Pages')],
                                    label='Export Type',
                                    widget=Select2Widget(attrs={'style': 'width: 100%;'}),
                                    required=True)

    export_single_file = forms.BooleanField(label='Export as Single File',
                                            required=False,
                                            help_text='Export each document/page as a separate file')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Export Documents'

    def get_dynamic_fields(self):
        return [
            Row(
                Column('export_type', css_class='form-group col-6 mb-0'),
                Column('export_single_file', css_class='form-group col-6 mb-0'),
                css_class='row form-row'
            )
        ]


class ExportCollectionsForm(BaseBatchForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Export Collection'

    def get_dynamic_fields(self):
        return []


class ExportProjectForm(BaseBatchForm):

    include_dictionaries = forms.BooleanField(label='Include Dictionaries',
                                              required=False,
                                              help_text='Include dictionaries in the export')

    include_media_files = forms.BooleanField(label='Include Media Files',
                                                required=False,
                                                help_text='Include media files in the export')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Export Project'

    def get_dynamic_fields(self):
        return [
            Row(
                Column('include_dictionaries', css_class='form-group col-6 mb-0'),
                Column('include_media_files', css_class='form-group col-6 mb-0'),
                css_class='row form-row'
            )
        ]


class ExportZenodoForm(BaseBatchForm):

    choose_repository = forms.ChoiceField(choices=[('new', 'Create New Repository')],
                                          label='Choose Repository',
                                          widget=Select2Widget(attrs={'style': 'width: 100%;'}),
                                          required=True)

    choose_export = forms.ModelChoiceField(queryset=None,
                                           label='Choose Export...',
                                           widget=Select2Widget(attrs={'style': 'width: 100%;'}),
                                           required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        existing_zenodo_uploads = get_zenodo_uploads(self.project)
        if existing_zenodo_uploads:
            existing_repositories = [(upload['id'], upload['metadata']['title']) for upload in existing_zenodo_uploads]
        else:
            existing_repositories = []
        self.fields['choose_repository'].choices += existing_repositories

        self.fields['choose_export'].queryset = self.project.export_set.all()

    def get_button_label(self):
        return 'Export Project to Zenodo'

    def get_dynamic_fields(self):
        return [
            Row(
                Column('choose_repository', css_class='form-group col-6 mb-0'),
                Column('choose_export', css_class='form-group col-6 mb-0'),
                css_class='row form-row'
            )
        ]


class ExportDataForm(forms.Form):
    """Form for exporting data."""

    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('excel', 'Excel')
    ]

    export_format = forms.ChoiceField(choices=FORMAT_CHOICES, label='Export Format')
    schema = forms.CharField(widget=forms.Textarea, required=False, label='Schema (Optional)',
                             help_text='Enter a JSON array of fields to include in the export')

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('export_format', css_class='form-group col-6 mb-0'),
                css_class='row form-row'
            ),
            Row(
                Column('schema', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Start Batch', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )
