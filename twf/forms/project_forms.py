from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Div, HTML
from django import forms
from django.db.models import Subquery
from django.forms import TextInput
from django.urls import reverse
from django_select2.forms import Select2MultipleWidget, Select2Widget

from twf.models import Project, Collection, Document, CollectionItem


class PasswordInputRetain(forms.PasswordInput):
    """A PasswordInput widget that retains the value when the form is re-rendered."""
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        # Set the value attribute if there's a value present
        if value:
            attrs = attrs or {}
            attrs['value'] = value
        return super().render(name, value, attrs, renderer)


class GeneralSettingsForm(forms.ModelForm):
    """Form for creating and updating general settings."""

    class Meta:
        model = Project
        fields = ['title', 'description', 'owner', 'members', 'selected_dictionaries']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'owner': Select2Widget(attrs={'style': 'width: 100%;'}),
            'members': Select2MultipleWidget(attrs={'style': 'width: 100%;'}),
            'selected_dictionaries': Select2MultipleWidget(attrs={'style': 'width: 100%;'}),
        }

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
                Column(
                    Row(
                        Column('owner', css_class='form-group col-12 mb-3'),
                        Column('members', css_class='form-group col-12 mb-3'),
                        css_class='row form-ow'), css_class='form-group col-4 mb-3'),
                Column('description', css_class='form-group col-8 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('selected_dictionaries', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Save Settings', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


class CredentialsForm(forms.ModelForm):
    """Form for creating and updating credentials."""

    openai_api_key = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'OpenAI API Key'}))
    openai_default_model = forms.CharField(required=False,
                                           widget=TextInput(attrs={'placeholder': 'OpenAI Default Model'}))

    genai_api_key = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'GenAI API Key'}))
    genai_default_model = forms.CharField(required=False,
                                          widget=TextInput(attrs={'placeholder': 'GenAI Default Model'}))

    anthropic_api_key = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Anthropic API Key'}))
    anthropic_default_model = forms.CharField(required=False,
                                              widget=TextInput(attrs={'placeholder': 'Anthropic Default Model'}))

    transkribus_username = forms.CharField(required=False,
                                           widget=TextInput(attrs={'placeholder': 'Transkribus Username'}))
    transkribus_password = forms.CharField(required=False,
                                           widget=forms.PasswordInput(attrs={'placeholder': 'Transkribus Password'}))

    geonames_username = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Geonames Username'}))

    class Meta:
        model = Project
        fields = ['conf_credentials']

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

        self.fields['transkribus_username'].initial = conf_credentials.get('transkribus', {}).get('username', '')
        self.fields['transkribus_password'].initial = conf_credentials.get('transkribus', {}).get('password', '')

        self.fields['geonames_username'].initial = conf_credentials.get('geonames', {}).get('username', '')

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
                    'GenAI',
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
                    'Geonames',
                    Row(Column('geonames_username', css_class='col-12')),
                    css_id='geonames'
                )
            ),
            Submit('submit', 'Save Settings', css_class='btn btn-dark')
        )

    def clean(self):
        """Clean and save credential data back into the JSONField `conf_credentials`."""
        cleaned_data = super().clean()
        self.instance.conf_credentials = {
            'openai': {'api_key': cleaned_data.get('openai_api_key')},
            'genai': {'api_key': cleaned_data.get('genai_api_key')},
            'anthropic': {'api_key': cleaned_data.get('anthropic_api_key')},
            'transkribus': {
                'username': cleaned_data.get('transkribus_username'),
                'password': cleaned_data.get('transkribus_password')
            },
            'geonames': {'username': cleaned_data.get('geonames_username')}
        }
        return cleaned_data


class TaskSettingsForm(forms.ModelForm):
    """Form for creating and updating task settings."""

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
    page_metadata_review = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Page Metadata Review'}))
    document_metadata_review = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Document Metadata Review'}))

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
        self.fields['google_sheet_valid_columns'].initial = conf_tasks.get('google_sheet', {}).get('valid_columns', '')
        self.fields['google_sheet_document_id_column'].initial = conf_tasks.get('google_sheet', {}).get('document_id_column', '')
        self.fields['google_sheet_document_title_column'].initial = conf_tasks.get('google_sheet', {}).get('document_title_column', '')

        self.fields['page_metadata_review'].initial = conf_tasks.get('metadata_review', {}).get('page_metadata_review', '')
        self.fields['document_metadata_review'].initial = conf_tasks.get('metadata_review', {}).get('document_metadata_review', '')

        self.helper.layout = Layout(
            TabHolder(
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
                    ), css_id='tag_types'
                ),
            ),
            Div(
                Submit('submit', 'Save Settings', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


class ExportSettingsForm(forms.ModelForm):
    """Form for creating and updating task settings."""

    # Define the fields for the form: Google Sheets Connection
    document_export_configuration = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))
    page_export_configuration = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5}))

    class Meta:
        model = Project
        fields = ['conf_export']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'

        # Populate the fields from `conf_export` JSON if data exists
        conf_export = self.instance.conf_export or {}
        self.fields['document_export_configuration'].initial = conf_export.get('document_export_configuration', '')
        self.fields['page_export_configuration'].initial = conf_export.get('page_export_configuration', '')

        self.helper.layout = Layout(
            TabHolder(
                Tab(
                    'Export Settings',
                    Row(
                        Column('document_export_configuration', css_class='col-6'),
                        Column('page_export_configuration', css_class='col-6'),
                    ), css_id='export_settings'
                ),
            ),
            Div(
                Submit('submit', 'Save Settings', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


class ProjectForm(forms.ModelForm):
    """Form for creating and updating projects."""
    class Meta:
        model = Project
        fields = ['collection_id', 'transkribus_job_id', 'job_download_url',
                  'owner', 'members', 'selected_dictionaries',
                  'tag_type_translator', 'ignored_tag_types',
                  'document_metadata_fields', 'page_metadata_fields']
        widgets = {
            'tag_type_translator': forms.Textarea(attrs={'rows': 3}),
            'ignored_tag_types': forms.Textarea(attrs={'rows': 3}),
            'document_metadata_fields': forms.Textarea(attrs={'rows': 3}),
            'field_metadata_fields': forms.Textarea(attrs={'rows': 3}),


        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.form_method = 'post'
        helper.form_class = 'form form-control'

        layout = helper.layout = Layout(
            Row(
                Div(
                    HTML(
                        '<strong>1.) General settings</strong>'
                    ),
                    css_class='col-12 mb-3'
                ),
                css_class='row form-row'
            ),
            Row(
                    Column('title', css_class='form-group col-4 mb-3'),
                    Column('collection_id', css_class='form-group col-4 mb-3'),
                    Column('transkribus_job_id', css_class='form-group col-4 mb-3'),
                    css_class='row form-row'
                ),
            Row(
                Column('job_download_url', css_class='form-group offset-4 col-8 mb-3'),
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
            Row(
                Div(
                    HTML(
                        '<strong>3.) Tag Settings</strong>'
                    ),
                    css_class='col-12 mb-3'
                ),
                css_class='row form-row'
            ),
            Row(
                Column('tag_type_translator', css_class='form-group col-6 mb-3'),
                Column('ignored_tag_types', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('document_metadata_fields', css_class='form-group col-6 mb-3'),
                Column('page_metadata_fields', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
        )

        self.helper = helper


class AIQueryDatabaseForm(forms.Form):
    """Form for querying the AI model with a question and documents."""

    documents = forms.ModelMultipleChoiceField(label='Documents', required=True,
                                               help_text='Please select the documents to query.',
                                               widget=Select2MultipleWidget(attrs={'style': 'width: 100%;'}),
                                               queryset=Document.objects.none())

    question = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label='Question',
                                 help_text='Please provide a question to ask the AI model.',
                                    required=True)

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super().__init__(*args, **kwargs)

        if project:
            self.fields['documents'].queryset = Document.objects.filter(project=project)

        helper = FormHelper()
        helper.form_method = 'post'
        helper.form_class = 'form form-control'

        layout = helper.layout = Layout(
            Row(
                Column('documents', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('question', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Div(
                HTML(f'<a href="{reverse("twf:project_ai_query")}" class="btn btn-dark color-light me-2">Clear</a>'),
                Submit('submit', 'Ask Question', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )
        helper.layout = layout
        self.helper = helper


class ProjectOpenAIForm(forms.Form):
    """Form for querying the OpenAI API with a question and documents."""

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super().__init__(*args, **kwargs)


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
                HTML(f'<a href="{reverse("twf:project_query")}" class="btn btn-dark color-light me-2">Clear</a>'),
                Submit('submit', 'Execute Query', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )
        helper.layout = layout
        self.helper = helper


class CollectionForm(forms.ModelForm):
    """Form for creating and updating collections."""

    class Meta:
        model = Collection
        fields = ['title', 'description']

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
                Column('description', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Save Collection', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


class CollectionAddDocumentForm(forms.Form):
    """Form for adding a document to a collection."""

    document = forms.ModelChoiceField(label='Document', required=True,
                                      help_text='Please select the document to add to the collection.',
                                      widget=Select2Widget(attrs={'style': 'width: 100%;'}),
                                      queryset=Document.objects.none())

    def __init__(self, *args, **kwargs):
        collection = kwargs.pop('collection')
        super().__init__(*args, **kwargs)

        if collection:
            # Filter documents that are not in the specified collection
            self.fields['document'].queryset = Document.objects.filter(
                project=collection.project
            ).exclude(
                id__in=Subquery(CollectionItem.objects.filter(collection=collection).values('document_id'))
            )

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'

        self.helper.layout = Layout(
            Row(
                Column('document', css_class='form-group'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Add Document', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )
