"""Forms for creating and updating documents."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Div, HTML
from django import forms
from django_select2.forms import Select2MultipleWidget, Select2Widget

from twf.models import Document, PageTag


class DocumentSearchForm(forms.Form):
    """Form for searching documents and their contents."""

    search_term = forms.CharField(
        label='Search Term', 
        required=False,
        help_text='Enter keywords to search for in documents',
        widget=forms.TextInput(attrs={'placeholder': 'Enter search term...', 'class': 'form-control'})
    )
    
    search_type = forms.ChoiceField(
        label='Search Type',
        choices=[
            ('all', 'All Fields'),
            ('title', 'Document Title'),
            ('document_id', 'Document ID'),
            ('metadata', 'Document Metadata'),
            ('workflow_remarks', 'Workflow Remarks'),
            ('document_text', 'Document Text'),
            ('tags', 'Document Tags')
        ],
        initial='all',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False,
    )
    
    status = forms.MultipleChoiceField(
        label='Document Status',
        choices=[
            ('open', 'Open'),
            ('needs_tk_work', 'Needs Work'),
            ('irrelevant', 'Irrelevant'),
            ('reviewed', 'Reviewed')
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    
    special_filters = forms.MultipleChoiceField(
        label='Special Filters',
        choices=[
            ('is_parked', 'Only Parked Documents'),
            ('has_pages', 'Has Pages'),
            ('has_tags', 'Has Tags'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    
    sort_by = forms.ChoiceField(
        label='Sort By', 
        choices=[
            ('title', 'Title A-Z'),
            ('-title', 'Title Z-A'),
            ('document_id', 'Document ID (Ascending)'),
            ('-document_id', 'Document ID (Descending)'),
            ('created_at', 'Oldest First'),
            ('-created_at', 'Newest First'),
        ], 
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
    )

    def __init__(self, *args, project=None, **kwargs):
        self.project = project
        super().__init__(*args, **kwargs)
        
        helper = FormHelper()
        helper.form_method = 'post'
        helper.form_class = 'form form-control'
        helper.form_id = 'document-search-form'
        
        # Add a hidden field to indicate this is a search submission
        helper.layout = Layout(
            HTML('<input type="hidden" name="search_submitted" value="true">'),
            Row(
                Column('search_term', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column(
                    HTML('<p class="text-muted">Select where to search for the term:</p>'),
                    'search_type', 
                    css_class='form-group col-12 mb-3'
                ),
                css_class='row form-row'
            ),
            Row(
                Column(
                    HTML('<p class="text-muted">Filter by document status:</p>'),
                    'status', 
                    css_class='form-group col-md-6 mb-3'
                ),
                Column(
                    HTML('<p class="text-muted">Additional filters:</p>'),
                    'special_filters', 
                    css_class='form-group col-md-6 mb-3'
                ),
                css_class='row form-row'
            ),
            Row(
                Column('sort_by', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('search', 'Search Documents', css_class='btn btn-dark'),
                HTML('<a href="{% url "twf:documents_search" %}" class="btn btn-outline-secondary ms-2">Reset Form</a>'),
                css_class='text-end pt-3'
            ),
        )
        self.helper = helper


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
