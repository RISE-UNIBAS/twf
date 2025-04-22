"""Forms for creating and updating project settings.
The settings views are separated into different forms for each section of the settings."""
import json
import re

from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Div, HTML
from django import forms
from django.forms import TextInput
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe
from django_select2.forms import Select2MultipleWidget, Select2Widget, Select2TagWidget
from markdown import markdown

from twf.clients import zenodo_client
from twf.models import Project, Prompt, Note


class CreateProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['title', 'description', 'collection_id', 'owner', 'members']
        widgets = { 'members': Select2MultipleWidget(attrs={'style': 'width: 100%;'}),
                    'owner': Select2Widget(attrs={'style': 'width: 100%;'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-6 mb-3'),
                Column('collection_id', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('description', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('owner', css_class='form-group col-6 mb-3'),
                Column('members', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Create Project', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )

class PasswordInputRetain(forms.PasswordInput):
    """A PasswordInput widget that retains the value when the form is re-rendered.
    This is used for password fields in the settings forms."""

    def render(self, name, value, attrs=None, renderer=None):
        """Render the widget with the value retained."""
        if value is None:
            value = ''
        # Set the value attribute if there's a value present
        if value:
            attrs = attrs or {}
            attrs['value'] = value
        return super().render(name, value, attrs, renderer)


class GeneralSettingsForm(forms.ModelForm):
    """Form for creating and updating general settings.

    General settings include the project title, description, owner, members, and selected dictionaries.
    
    It enforces the following restrictions:
    1. Project owners cannot change ownership to another user
    2. Project members cannot remove themselves from the project
    """

    class Meta:
        model = Project
        fields = ['title', 'description', 'owner', 'members']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'owner': Select2Widget(attrs={'style': 'width: 100%;'}),
            'members': Select2MultipleWidget(attrs={'style': 'width: 100%;'}),
        }

    def __init__(self, *args, **kwargs):
        # Get the current user from kwargs
        self.current_user = kwargs.pop('current_user', None)
        
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'
        
        instance = kwargs.get('instance')
        
        # If the current user is the owner, disable the owner field
        if self.current_user and instance and hasattr(instance, 'owner') and hasattr(self.current_user, 'profile'):
            if instance.owner == self.current_user.profile:
                self.fields['owner'].disabled = True
                self.fields['owner'].help_text = "You cannot change ownership as the current owner."
        
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column(
                    Row(
                        Column('owner', css_class='form-group col-12 mb-3'),
                        Column('members', css_class='form-group col-12 mb-3'),
                        css_class='row form-ow'), css_class='form-group col-4 mb-3'),
                Column('description', css_class='form-group col-8 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Save Settings', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )
        
    def clean(self):
        """
        Validate that:
        1. The current user is not changing ownership if they are the owner
        2. The current user is not removing themselves from members if they are a member
        """
        cleaned_data = super().clean()
        
        if not self.current_user or not hasattr(self.current_user, 'profile'):
            return cleaned_data
            
        # Check if owner is being changed by the current owner
        if self.instance and self.instance.owner == self.current_user.profile:
            # Ensure owner hasn't been changed
            if 'owner' in cleaned_data and cleaned_data['owner'] != self.current_user.profile:
                self.add_error('owner', "As the current owner, you cannot transfer ownership to another user.")
        
        # Check if the current user is removing themselves from members
        if self.instance and self.current_user.profile in self.instance.members.all():
            members_after = cleaned_data.get('members', [])
            if self.current_user.profile not in members_after:
                # Add the current user back to the members list
                members_list = list(members_after)
                members_list.append(self.current_user.profile)
                cleaned_data['members'] = members_list
                self.add_error('members', "You cannot remove yourself from the project members.")
        
        return cleaned_data


class CredentialsForm(forms.ModelForm):
    """Form for creating and updating credentials."""

    active_tab = forms.CharField(widget=forms.HiddenInput(), required=False)

    openai_api_key = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'OpenAI API Key'}))
    openai_default_model = forms.CharField(required=False,
                                           widget=TextInput(attrs={'placeholder': 'OpenAI Default Model'}))

    genai_api_key = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Google API Key'}))
    genai_default_model = forms.CharField(required=False,
                                          widget=TextInput(attrs={'placeholder': 'Google Default Model'}))

    anthropic_api_key = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Anthropic API Key'}))
    anthropic_default_model = forms.CharField(required=False,
                                              widget=TextInput(attrs={'placeholder': 'Anthropic Default Model'}))

    mistral_api_key = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Mistral API Key'}))
    mistral_default_model = forms.CharField(required=False,
                                            widget=TextInput(attrs={'placeholder': 'Mistral Default Model'}))

    transkribus_username = forms.CharField(required=False,
                                           widget=TextInput(attrs={'placeholder': 'Transkribus Username'}))
    transkribus_password = forms.CharField(required=False,
                                           widget=PasswordInputRetain(attrs={'placeholder': 'Transkribus Password'}))

    geonames_username = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Geonames Username'}))

    zenodo_token = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Zenodo Access Token'}))

    class Meta:
        model = Project
        fields = ['conf_credentials', 'active_tab']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate the fields from `conf_credentials` JSON if data exists
        conf_credentials = self.instance.conf_credentials or {}
        self.fields['openai_api_key'].initial = conf_credentials.get('openai', {}).get('api_key', '')
        self.fields['openai_default_model'].initial = conf_credentials.get('openai', {}).get('default_model', '')

        self.fields['genai_api_key'].initial = conf_credentials.get('genai', {}).get('api_key', '')
        self.fields['genai_default_model'].initial = conf_credentials.get('genai', {}).get('default_model', '')

        self.fields['anthropic_api_key'].initial = conf_credentials.get('anthropic', {}).get('api_key', '')
        self.fields['anthropic_default_model'].initial = conf_credentials.get('anthropic', {}).get('default_model', '')

        self.fields['mistral_api_key'].initial = conf_credentials.get('mistral', {}).get('api_key', '')
        self.fields['mistral_default_model'].initial = conf_credentials.get('mistral', {}).get('default_model', '')

        self.fields['transkribus_username'].initial = conf_credentials.get('transkribus', {}).get('username', '')
        self.fields['transkribus_password'].initial = conf_credentials.get('transkribus', {}).get('password', '')

        self.fields['geonames_username'].initial = conf_credentials.get('geonames', {}).get('username', '')

        self.fields['zenodo_token'].initial = conf_credentials.get('zenodo', {}).get('zenodo_token', '')

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'
        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    'Transkribus',
                    Row(
                        Column('transkribus_username', css_class='col-6'),
                        Column('transkribus_password', css_class='col-6')
                    ), css_id='transkribus'
                ),
                Tab(
                    'OpenAI',
                    Row(Column('openai_api_key', css_class='col-12')),
                    Row(Column('openai_default_model', css_class='col-12')),
                    css_id='openai'
                ),
                Tab(
                    'Google',
                    Row(Column('genai_api_key', css_class='col-12')),
                    Row(Column('genai_default_model', css_class='col-12')),
                    css_id='genai'
                ),
                Tab(
                    'Anthropic',
                    Row(Column('anthropic_api_key', css_class='col-12')),
                    Row(Column('anthropic_default_model', css_class='col-12')),
                    css_id='anthropic'
                ),
                Tab(
                    'Mistral',
                    Row(Column('mistral_api_key', css_class='col-12')),
                    Row(Column('mistral_default_model', css_class='col-12')),
                    css_id='mistral'
                ),
                Tab(
                    'Geonames',
                    Row(Column('geonames_username', css_class='col-12')),
                    css_id='geonames'
                ),
                Tab(
                    'Zenodo',
                    Row(Column('zenodo_token', css_class='col-12')),
                    css_id='zenodo'
                )
            ),
            Div(
                Submit('submit', 'Save Settings', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            ),
            'active_tab'
        )

    def clean(self):
        """Clean and save credential data back into the JSONField `conf_credentials`."""
        cleaned_data = super().clean()
        self.instance.conf_credentials = {
            'openai': {'api_key': cleaned_data.get('openai_api_key'),
                       'default_model': cleaned_data.get('openai_default_model')},
            'genai': {'api_key': cleaned_data.get('genai_api_key'),
                      'default_model': cleaned_data.get('genai_default_model')},
            'anthropic': {'api_key': cleaned_data.get('anthropic_api_key'),
                          'default_model': cleaned_data.get('anthropic_default_model')},
            'mistral': {'api_key': cleaned_data.get('mistral_api_key'),
                        'default_model': cleaned_data.get('mistral_default_model')},
            'transkribus': {
                'username': cleaned_data.get('transkribus_username'),
                'password': cleaned_data.get('transkribus_password')
            },
            'geonames': {'username': cleaned_data.get('geonames_username')},
            'zenodo': {'zenodo_token': cleaned_data.get('zenodo_token')}
        }
        return cleaned_data


class TaskSettingsForm(forms.ModelForm):
    """Form for creating and updating task settings."""

    active_tab = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Define the fields for the form: Google Sheets Connection
    google_sheet_id = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Google Sheet ID'}),
                                      help_text='Copy the part as indicated:'
                                                'https://docs.google.com/spreadsheets/d/<b>GOOGLE_SHEET_ID</b>/edit')
    google_sheet_range = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Google Sheet Range'}),
                                         )
    google_sheet_valid_columns = forms.CharField(required=False,
                                                 widget=TextInput(attrs={'placeholder': 'Google Sheet Valid Columns'}))
    google_sheet_document_id_column = forms.CharField(required=False,
                                                      widget=TextInput(
                                                          attrs={
                                                              'placeholder': 'Google Sheet Document ID Column'}))
    google_sheet_document_title_column = forms.CharField(required=False,
                                                         widget=TextInput(
                                                             attrs={
                                                                 'placeholder': 'Google Sheet Document Title Column'}))

    # Define the fields for the form: Metadata Review Settings
    page_metadata_review = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))
    document_metadata_review = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))

    # Define the fields for the form: Date normalization settings
    date_input_format = forms.ChoiceField(required=False,
                                          choices=[('', 'Select Date Format'),
                                                   ('auto', 'Auto Detect'),
                                                   ('DMY', 'DMY'), ('YMD', 'YMD')],
                                          widget=Select2Widget(attrs={'style': 'width: 100%;'}))
    resolve_to_date = forms.ChoiceField(required=False, label="Resolve to Precision",
                                        choices=[('', 'Select Resolve to Precision'),
                                                 ('day', 'Day'),
                                                 ('month', 'Month'),
                                                 ('year', 'Year')],
                                        widget=Select2Widget(attrs={'style': 'width: 100%;'}))

    # Define the fields for the form: Tag Type Settings
    tag_type_translator = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}),
                                            help_text='Enter a JSON object to map tag types to a common format')
    ignored_tag_types = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}),
                                        help_text='Enter a JSON array of tag types to ignore')

    class Meta:
        model = Project
        fields = ['conf_tasks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'

        # Populate the fields from `conf_tasks` JSON if data exists
        conf_tasks = self.instance.conf_tasks or {}
        self.fields['google_sheet_id'].initial = conf_tasks.get('google_sheet', {}).get('sheet_id', '')
        self.fields['google_sheet_range'].initial = conf_tasks.get('google_sheet', {}).get('range', '')
        self.fields['google_sheet_valid_columns'].initial = conf_tasks.get('google_sheet',
                                                                           {}).get('valid_columns', '')
        self.fields['google_sheet_document_id_column'].initial = conf_tasks.get('google_sheet',
                                                                                {}).get('document_id_column', '')
        self.fields['google_sheet_document_title_column'].initial = conf_tasks.get('google_sheet',
                                                                                   {}).get('document_title_column', '')

        self.fields['page_metadata_review'].initial = conf_tasks.get('metadata_review',
                                                                     {}).get('page_metadata_review', '')
        self.fields['document_metadata_review'].initial = conf_tasks.get('metadata_review',
                                                                         {}).get('document_metadata_review', '')

        self.fields['date_input_format'].initial = conf_tasks.get('date_normalization',
                                                                  {}).get('date_input_format', '')
        self.fields['resolve_to_date'].initial = conf_tasks.get('date_normalization',
                                                                {}).get('resolve_to_date', '')

        self.fields['tag_type_translator'].initial = conf_tasks.get('tag_types', {}).get('tag_type_translator', '')
        self.fields['ignored_tag_types'].initial = conf_tasks.get('tag_types', {}).get('ignored_tag_types', '')

        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    'Date Normalization Settings',
                    Row(
                        Column('date_input_format', css_class='col-6'),
                        Column('resolve_to_date', css_class='col-6'),
                    ), css_id='date_normalization'
                ),
                Tab(
                    'Google Sheets Connection',
                    Row(
                        Column('google_sheet_id', css_class='col-12'),
                        ),
                    Row(
                        Column('google_sheet_range', css_class='col-6'),
                        Column('google_sheet_valid_columns', css_class='col-6'),
                        ),
                    Row(
                        Column('google_sheet_document_id_column', css_class='col-6'),
                        Column('google_sheet_document_title_column', css_class='col-6'),
                    ), css_id='google_sheets'
                ),
                Tab(
                    'Metadata Review Settings',
                    Row(
                        Column('page_metadata_review', css_class='col-6'),
                        Column('document_metadata_review', css_class='col-6'),
                    ), css_id='metadata_review'
                ),
                Tab(
                    'Tag Type Settings',
                    Row(
                        Column('tag_type_translator', css_class='col-6'),
                        Column('ignored_tag_types', css_class='col-6'),
                    ), css_id='tag_types'
                ),
            ),
            Div(
                Submit('submit', 'Save Settings', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            ),
            'active_tab'
        )

    def clean(self):
        cleaned_data = super().clean()

        # Grab values from cleaned_data
        sheet_id = cleaned_data.get("google_sheet_id")
        sheet_range = cleaned_data.get("google_sheet_range")
        valid_cols = cleaned_data.get("google_sheet_valid_columns")
        doc_id_col = cleaned_data.get("google_sheet_document_id_column")
        doc_title_col = cleaned_data.get("google_sheet_document_title_column")

        # Require sheet_id if any other field is set
        if (sheet_range or valid_cols or doc_id_col or doc_title_col) and not sheet_id:
            self.add_error("google_sheet_id", "This field is required if other Google Sheet fields are set.")

        # Validate sheet range using regex
        # Format: Sheet1!A1:D100 or A1:D100
        if sheet_range:
            pattern = r"^([a-zA-Z0-9_ ]+!)?[A-Z]+\d+(:[A-Z]+\d+)?$"
            if not re.match(pattern, sheet_range):
                self.add_error("google_sheet_range", "Invalid range format. Use A1:B10 or Sheet1!A1:B10.")

        # Validate valid columns as comma-separated list
        if valid_cols:
            cols = [c.strip() for c in valid_cols.split(",")]
            if not all(cols):
                self.add_error("google_sheet_valid_columns", "Please enter a comma-separated list of column names.")
            elif any(" " in col for col in cols):
                self.add_error("google_sheet_valid_columns", "Column names should not contain spaces.")

        # Validate doc_id_col and doc_title_col to be non-empty and space-free (if filled)
        if doc_id_col and " " in doc_id_col:
            self.add_error("google_sheet_document_id_column", "Column name must not contain spaces.")
        if doc_title_col and " " in doc_title_col:
            self.add_error("google_sheet_document_title_column", "Column name must not contain spaces.")

        # Validate all metadata_review and tag_type fields are valid JSON
        json_fields = [
            ("page_metadata_review", "Page Metadata Review"),
            ("document_metadata_review", "Document Metadata Review"),
            ("tag_type_translator", "Tag Type Translator"),
            ("ignored_tag_types", "Ignored Tag Types")
        ]

        for field_name, label in json_fields:
            raw_value = cleaned_data.get(field_name)
            if raw_value:
                try:
                    json.loads(raw_value)
                except json.JSONDecodeError:
                    self.add_error(field_name, f"{label} must be valid JSON.")


        # Reconstruct JSON field
        self.instance.conf_tasks = {
            "google_sheet": {
                "sheet_id": sheet_id,
                "range": sheet_range,
                "valid_columns": valid_cols,
                "document_id_column": doc_id_col,
                "document_title_column": doc_title_col
            },
            "metadata_review": {
                "page_metadata_review": cleaned_data.get("page_metadata_review"),
                "document_metadata_review": cleaned_data.get("document_metadata_review")
            },
            "date_normalization": {
                "date_input_format": cleaned_data.get("date_input_format"),
                "resolve_to_date": cleaned_data.get("resolve_to_date")
            },
            "tag_types": {
                "tag_type_translator": cleaned_data.get("tag_type_translator"),
                "ignored_tag_types": cleaned_data.get("ignored_tag_types")
            }
        }

        return cleaned_data


class ExportSettingsForm(forms.ModelForm):
    """Form for creating and updating task settings."""

    # Define the fields for the form: Google Sheets Connection
    project_export_configuration = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))
    document_export_configuration = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))
    page_export_configuration = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))

    class Meta:
        model = Project
        fields = ['conf_export']

    def __init__(self, *args, **kwargs):
        show_help = kwargs.pop('show_help', True)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'

        if not show_help:
            self.helper.form_class += ' h-100'

        # Populate the fields from `conf_export` JSON if data exists
        conf_export = self.instance.conf_export or {}
        self.fields['project_export_configuration'].initial = conf_export.get('project_export_configuration', '')
        self.fields['document_export_configuration'].initial = conf_export.get('document_export_configuration', '')
        self.fields['page_export_configuration'].initial = conf_export.get('page_export_configuration', '')

        help_text_html = ('Enter a JSON object to configure the export settings. '
                          'For each output field, you can specify the source field '
                          'from the document or page metadata.<br/>Example: <br/>'
                          '<code>{</code><br/>'
                          '<code>&nbsp;&nbsp;"id": {"value": "<b>{</b>metadata_key<b>}</b>"}</code><br/>'
                          '<code>&nbsp;&nbsp;"project": {"value": "Static project title"}</code><br/>'
                          '<code>&nbsp;&nbsp;"tags": {"value": ""}</code><br/>'
                          '<code>}</code><br/>')

        static_keys_html = render_to_string('twf/forms/static_keys_tab.html')

        self.helper.layout = Layout()
        tab_holder = TabHolder(
                Tab(
                    'Document Export Settings',
                    Row(
                        Column('document_export_configuration', css_class='col-12'),
                    ), css_id='document_export_settings'
                ),
                Tab(
                    'Page Export Settings',
                    Row(
                        Column('page_export_configuration', css_class='col-12'),
                    ), css_id='page_export_settings'
                ),
                Tab(
                    'Project Export Settings',
                    Row(
                        Column('project_export_configuration', css_class='col-12'),
                    ), css_id='project_export_settings'
                )
        )

        if show_help:
            tab_holder.append(
                Tab(
                    'Help',
                    Row(
                        Column(HTML(help_text_html), css_class='col-12'),
                    ), css_id='export_settings_help'
                )
            )
            tab_holder.append(
                Tab(
                    'Additional Data Fields',
                    Row(
                        Column(HTML(static_keys_html), css_class='col-12'),
                    ), css_id='export_static_keys'
                ),
            )

        self.helper.layout.append(tab_holder)
        self.helper.layout.append(
            Div(
                Submit('submit', 'Save Settings', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )

    def clean(self):
        """Clean and save export data back into the JSONField `conf_export`."""
        cleaned_data = super().clean()
        self.instance.conf_export = {
            'project_export_configuration': cleaned_data.get('project_export_configuration'),
            'document_export_configuration': cleaned_data.get('document_export_configuration'),
            'page_export_configuration': cleaned_data.get('page_export_configuration')
        }
        return cleaned_data


class RepositorySettingsForm(forms.ModelForm):
    """Form for updating repository settings."""

    license = forms.ChoiceField(
        choices=zenodo_client.LICENSE_CHOICES,
        widget=Select2Widget(attrs={'style': 'width: 100%;'}),
        required=True,
    )

    keywords = forms.JSONField(
        widget=Select2TagWidget(attrs={
            'style': 'width: 100%;', 
            'data-token-separators': json.dumps([','])  # Only use comma as separator
        }),
        required=False,
    )

    workflow_description_preview = forms.CharField(
        required=False,
    )

    class Meta:
        model = Project
        fields = ['keywords', 'license', 'version', 'workflow_description']
        widgets = {
            'version': TextInput(attrs={'placeholder': 'Version'}),
            'workflow_description': forms.Textarea(attrs={'rows': 20, 'id': 'workflow_description'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'

        if self.instance and self.instance.keywords:
            if isinstance(self.instance.keywords, str):
                try:
                    self.initial['keywords'] = json.loads(self.instance.keywords)  # Ensure it's a list
                except json.JSONDecodeError:
                    self.initial['keywords'] = []
            else:
                self.initial['keywords'] = self.instance.keywords  # Expecting a list

            # Add the value as a data attribute
            self.fields['keywords'].widget.attrs['data-value'] = json.dumps(self.initial['keywords'])

        self.helper.layout = Layout(
            Row(
                Column('version', css_class='form-group col-6 mb-3'),
                Column('license', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('keywords', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column(HTML(
                    '<button type="button" class="btn btn-secondary mt-2" id="generate_md">Generate Default</button>'
                ), css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('workflow_description', css_class='form-group col-6 mb-3'),
                Column('workflow_description_preview', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Save Settings', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        if 'workflow_description' in cleaned_data:
            cleaned_data['workflow_description_preview'] = mark_safe(
                markdown(cleaned_data['workflow_description'])
            )

        if 'keywords' in cleaned_data:
            if isinstance(cleaned_data['keywords'], str):
                try:
                    cleaned_data['keywords'] = json.loads(cleaned_data['keywords'])  # Convert to list
                except json.JSONDecodeError:
                    cleaned_data['keywords'] = []  # Default to an empty list if parsing fails
            elif not cleaned_data['keywords']:
                cleaned_data['keywords'] = []  # Ensure it's an empty list instead of None

        return cleaned_data



class QueryDatabaseForm(forms.Form):
    """Form for querying the database with a SQL query."""

    query = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label='Query',
                            help_text='Please provide a SQL query to execute on the database.'
                                      'Only SELECT queries are allowed.',
                            initial='SELECT * FROM twf_pagetag LIMIT 100 OFFSET 0;',
                            required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.form_method = 'post'
        helper.form_class = 'form form-control'

        layout = helper.layout = Layout(
            Row(
                Column('query', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Div(
                HTML(f'<a href="{reverse("twf:project_query")}" class="btn btn-dark '
                     f'color-light me-2">Clear</a>'),
                Submit('submit', 'Execute Query', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )
        helper.layout = layout
        self.helper = helper


class PromptForm(forms.ModelForm):
    """Form for creating and updating prompts."""

    class Meta:
        model = Prompt
        fields = ['system_role', 'prompt']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'
        self.helper.layout = Layout(
            Row(
                Column('system_role', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('prompt', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Save Prompt', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


class NoteForm(forms.ModelForm):
    """Form for creating and updating prompts."""

    class Meta:
        model = Note
        fields = ['title', 'note']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('note', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Save Note', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )