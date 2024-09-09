from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Div, HTML
from django import forms
from django.db.models import Subquery
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


class ProjectForm(forms.ModelForm):
    """Form for creating and updating projects."""
    class Meta:
        model = Project
        fields = ['title', 'description', 'collection_id', 'transkribus_job_id', 'job_download_url',
                  'metadata_google_sheet_id', 'metadata_google_sheet_range', 'metadata_google_doc_id_column',
                  'metadata_google_title_column', 'metadata_google_valid_columns',
                  'owner', 'members', 'selected_dictionaries',
                  'tag_type_translator', 'ignored_tag_types',
                  'transkribus_username', 'transkribus_password',
                  'geonames_username', 'openai_api_key',
                  'document_metadata_fields', 'page_metadata_fields']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'owner': Select2Widget(attrs={'style': 'width: 100%;'}),
            'members': Select2MultipleWidget(attrs={'style': 'width: 100%;'}),
            'metadata_google_valid_columns': forms.Textarea(attrs={'rows': 5}),
            'tag_type_translator': forms.Textarea(attrs={'rows': 3}),
            'ignored_tag_types': forms.Textarea(attrs={'rows': 3}),
            'transkribus_password': PasswordInputRetain(),
            'selected_dictionaries': Select2MultipleWidget(attrs={'style': 'width: 100%;'}),
            'document_metadata_fields': forms.Textarea(attrs={'rows': 3}),
            'field_metadata_fields': forms.Textarea(attrs={'rows': 3})
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
                        '<strong>2.) Google Sheets Connection</strong>'
                    ),
                    css_class='col-12 mb-3'
                ),
                css_class='row form-row'
            ),
            Row(
                Column('metadata_google_sheet_id', css_class='form-group col-6 mb-3'),
                Column('metadata_google_sheet_range', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column(
                    Row(
                        Column('metadata_google_doc_id_column', css_class='form-group col-12 mb-3'),
                        Column('metadata_google_title_column', css_class='form-group col-12 mb-3'),
                        css_class='row form-ow'), css_class='form-group col-4 mb-3'),
                Column('metadata_google_valid_columns', css_class='form-group col-8 mb-3'),
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
                Div(
                    HTML(
                        '<strong>4.) Dictionary Settings</strong>'
                    ),
                    css_class='col-12 mb-3'
                ),
                css_class='row form-row'
            ),
            Row(
                Column('selected_dictionaries', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Div(
                    HTML(
                        '<strong>5.) Authentication data</strong>'
                    ),
                    css_class='col-12 mb-3'
                ),
                css_class='row form-row'
            ),
            Row(
                Column('transkribus_username', css_class='form-group col-6 mb-3'),
                Column('transkribus_password', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('geonames_username', css_class='form-group col-6 mb-3'),
                Column('openai_api_key', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Div(
                    HTML(
                        '<strong>6.) Metadata Settings</strong>'
                    ),
                    css_class='col-12 mb-3'
                ),
                css_class='row form-row'
            ),
            Row(
                Column('document_metadata_fields', css_class='form-group col-6 mb-3'),
                Column('page_metadata_fields', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Save Settings', css_class='btn btn-dark'),
                css_class='text-end pt-3'
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


class DocumentForm(forms.ModelForm):
    """Form for creating and updating documents."""

    class Meta:
        model = Document
        fields = ['title', 'document_id', 'metadata']
        widgets = {
            'metadata': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.form_method = 'post'
        helper.form_class = 'form form-control'

        layout = helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-6 mb-3'),
                Column('document_id', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('metadata', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Create Document', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            ),
        )

        self.helper = helper


class BatchOpenAIForm(forms.Form):
    CHOICES = [
        ('documents', 'Documents'),
        ('collection', 'Collection')
    ]

    selection = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect, label="Choose Type")
    role_description = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'placeholder': 'Describe the role here...'
    }), label="Role Description")
    prompt = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Enter your prompt here...'
    }), label="Prompt")

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super().__init__(*args, **kwargs)
        helper = FormHelper()
        helper.form_method = 'post'
        helper.form_class = 'form form-control'
        helper.form_id = 'batch-openai-form'

        helper.layout = Layout(
            Row(
                Column('selection', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('role_description', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('prompt', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Start Project Batch', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            ),
        )

        self.helper = helper
