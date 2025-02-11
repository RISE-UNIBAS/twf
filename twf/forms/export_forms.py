""" This module contains forms for exporting data from the application. """
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Column, Div, Row
from django import forms
from django_select2.forms import Select2Widget

from twf.clients.zenodo_client import get_zenodo_uploads
from twf.forms.base_batch_forms import BaseBatchForm


class ExportDocumentsForm(BaseBatchForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Export Documents'

    def get_dynamic_fields(self):
        return []


class ExportCollectionsForm(BaseBatchForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Export Collection'

    def get_dynamic_fields(self):
        return []


class ExportProjectForm(BaseBatchForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Export Project'

    def get_dynamic_fields(self):
        return []


class ExportZenodoForm(BaseBatchForm):

    choose_repository = forms.ChoiceField(choices=[('new', 'Create New Repository')],
                                          label='Choose Repository',
                                          widget=Select2Widget(attrs={'style': 'width: 100%;'}),
                                          required=True)

    choose_export = forms.ChoiceField(choices=[],
                                      label='Choose Export...',
                                      widget=Select2Widget(attrs={'style': 'width: 100%;'}),
                                      required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        existing_zenodo_uploads = get_zenodo_uploads(self.project)
        existing_repositories = [(upload['id'], upload['metadata']['title']) for upload in existing_zenodo_uploads]
        self.fields['choose_repository'].choices += existing_repositories

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
