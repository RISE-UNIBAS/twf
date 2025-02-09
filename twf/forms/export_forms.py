""" This module contains forms for exporting data from the application. """
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Column, Div, Row
from django import forms

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
