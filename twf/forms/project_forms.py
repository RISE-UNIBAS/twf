"""Forms for creating and updating project settings."""
from crispy_forms.bootstrap import TabHolder, Tab
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Div, HTML
from django import forms
from django.db.models import Subquery
from django.forms import TextInput
from django.template.loader import render_to_string
from django.urls import reverse
from django_select2.forms import Select2MultipleWidget, Select2Widget

from twf.models import Project, Collection, Document, CollectionItem, User, Task


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

    active_tab = forms.CharField(widget=forms.HiddenInput(), required=False)

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
                                           widget=PasswordInputRetain(attrs={'placeholder': 'Transkribus Password'}))

    geonames_username = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Geonames Username'}))

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
            'transkribus': {
                'username': cleaned_data.get('transkribus_username'),
                'password': cleaned_data.get('transkribus_password')
            },
            'geonames': {'username': cleaned_data.get('geonames_username')}
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
    date_input_format = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Date Input Format'}))
    resolve_to_date = forms.CharField(required=False, widget=TextInput(attrs={'placeholder': 'Resolve to Precision'}))

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
        """Clean and save task data back into the JSONField `conf_tasks`."""
        cleaned_data = super().clean()
        self.instance.conf_tasks = {
            'google_sheet': {
                'sheet_id': cleaned_data.get('google_sheet_id'),
                'range': cleaned_data.get('google_sheet_range'),
                'valid_columns': cleaned_data.get('google_sheet_valid_columns'),
                'document_id_column': cleaned_data.get('google_sheet_document_id_column'),
                'document_title_column': cleaned_data.get('google_sheet_document_title_column')
            },
            'metadata_review': {
                'page_metadata_review': cleaned_data.get('page_metadata_review'),
                'document_metadata_review': cleaned_data.get('document_metadata_review')
            },
            'date_normalization': {
                'date_input_format': cleaned_data.get('date_input_format'),
                'resolve_to_date': cleaned_data.get('resolve_to_date')
            },
            'tag_types': {
                'tag_type_translator': cleaned_data.get('tag_type_translator'),
                'ignored_tag_types': cleaned_data.get('ignored_tag_types')
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
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form form-control'

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

        self.helper.layout = Layout(
            TabHolder(
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
                ),
                Tab(
                    'Help',
                    Row(
                        Column(HTML(help_text_html), css_class='col-12'),
                    ), css_id='export_settings_help'
                ),
                Tab(
                    'Additional Data Fields',
                    Row(
                        Column(HTML(static_keys_html), css_class='col-12'),
                    ), css_id='export_static_keys'
                ),
            ),
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
                HTML(f'<a href="{reverse("twf:project_ai_query")}" class="btn btn-dark '
                     f'color-light me-2">Clear</a>'),
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
                HTML(f'<a href="{reverse("twf:project_query")}" class="btn btn-dark '
                     f'color-light me-2">Clear</a>'),
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



class TaskFilterForm(forms.Form):
    """Form for filtering tasks."""

    started_by = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Started by",
    )
    status = forms.ChoiceField(
        choices=[("", "All")] + Task.TASK_STATUS_CHOICES,
        required=False,
        label="Status",
    )
    date_range = forms.ChoiceField(
        choices=[
            ("", "All time"),
            ("last_week", "Last week"),
            ("last_month", "Last month"),
            ("last_year", "Last year"),
        ],
        required=False,
        label="Date Range",
    )


class PromptFilterForm(forms.Form):
    """Form for filtering prompts."""

    system_role = forms.CharField(
        required=False,
        label="System Role",
        widget=forms.TextInput(attrs={"placeholder": "Enter system role"}),
    )
    has_document_context = forms.ChoiceField(
        choices=[("", "All"), ("yes", "Yes"), ("no", "No")],
        required=False,
        label="Document Context",
    )
    has_page_context = forms.ChoiceField(
        choices=[("", "All"), ("yes", "Yes"), ("no", "No")],
        required=False,
        label="Page Context",
    )
    has_collection_context = forms.ChoiceField(
        choices=[("", "All"), ("yes", "Yes"), ("no", "No")],
        required=False,
        label="Collection Context",
    )
