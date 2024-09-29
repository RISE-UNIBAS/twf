""" This module contains forms for exporting data from the application. """
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Column, Div, Row
from django import forms

from twf.models import Project


class ExportConfigForm(forms.ModelForm):
    """Form for configuring export settings."""

    class Meta:
        model = Project
        fields = ['document_export_configuration', 'page_export_configuration']
        widgets = {
            'document_export_configuration': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
            'page_export_configuration': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
        }
        labels = {
            'document_export_configuration': 'Document Export Configuration',
            'page_export_configuration': 'Page Export Configuration',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'

        self.helper.layout = Layout(
            Row(
                Column('document_export_configuration', css_class='form-group col-6 mb-3'),
                Column('page_export_configuration', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('test', 'Test', css_class='btn btn-dark me-2'),
                Submit('export', 'Export', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


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
