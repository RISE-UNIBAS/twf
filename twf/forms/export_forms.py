""" This module contains forms for exporting data from the application. """
import json

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Column, Div, Row, Hidden, Button, HTML
from django import forms
from django_select2.forms import Select2Widget

from twf.clients.zenodo_client import get_zenodo_uploads
from twf.forms.base_batch_forms import BaseBatchForm
from twf.models import ExportConfiguration, Export


class ExportConfigurationForm(forms.ModelForm):

    description = forms.CharField(
        label='Description',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Optional description of the export configuration.'
    )

    config = forms.CharField(
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = ExportConfiguration
        fields = ['name', 'description', 'export_type', 'output_format', 'config', 'is_default']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically adjust output format choices based on export_type
        if 'export_type' in self.data:
            export_type = self.data.get('export_type')
        elif self.instance and self.instance.pk:
            export_type = self.instance.export_type
        else:
            export_type = None

        allowed_formats = {
            'document': ['json'],
            'page': ['json'],
            'collection': ['json'],
            'dictionary': ['json', 'csv'],
            'tag_report': ['json', 'csv'],
        }

        if export_type:
            choices = [(fmt, fmt.upper()) for fmt in allowed_formats.get(export_type, ['json'])]
            self.fields['output_format'].choices = choices
        else:
            # Default to json
            self.fields['output_format'].choices = [('json', 'JSON')]

        if 'config' in self.initial and isinstance(self.initial['config'], dict):
            self.initial['config'] = json.dumps(self.initial['config'])

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'export-configuration-form'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-6 mb-0'),
                Column('is_default', css_class='form-group col-6 mb-0'),
                css_class='row form-row'
            ),
            Row(
                Column('description', css_class='form-group col-6 mb-0'),
                Column(
                    'export_type', 'output_format', css_class='form-group col-6 mb-0',
                ),
                css_class='row form-row'
            ),
            Div(
                Div(id="export-config-editor"),
                css_class="form-group col-12 mb-0"
            ),
            # Hidden config field (still required to submit)
            'config',
            Div(
                HTML('<button type="submit" class="btn btn-dark">Save Export Configuration</button>'),
                css_class='text-end pt-3'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        config = cleaned_data.get('config')
        if not config:
            raise forms.ValidationError("Configuration is required.")
        return cleaned_data



class RunExportForm(BaseBatchForm):

    export_conf = forms.ModelChoiceField(label='Export Configuration',
                                         widget=Select2Widget(attrs={'style': 'width: 100%;'}),
                                         required=True,
                                         queryset=ExportConfiguration.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['export_conf'].queryset = ExportConfiguration.objects.filter(project=self.project)

    def get_button_label(self):
        return 'Run Export'

    def get_dynamic_fields(self):
        return [
            Row(
                Column('export_conf', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            )
        ]


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

        self.fields['choose_export'].queryset = Export.objects.filter(export_configuration__project=self.project)

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
