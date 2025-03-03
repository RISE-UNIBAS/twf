"""Forms for creating and updating documents."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Div
from django import forms
from django_select2.forms import Select2MultipleWidget, Select2Widget

from twf.models import Document


class DocumentSearchForm(forms.Form):
    """Form for searching documents."""

    search_term = forms.CharField(label='Search', required=False,
                                  help_text='Search for any term, you can use regular expressions.')
    search_in = forms.MultipleChoiceField(label='Search', choices=[
        ('title', 'Document Title'),
        ('document_id', 'Transkribus Doc ID'),
        ('metadata', 'Metadata'),
        ('workflow_remarks', 'Workflow Remarks'),
        ('document_text', 'Document Text'),
    ], widget=Select2MultipleWidget(attrs={'data-placeholder': 'Search in'}),
       required=False,
       help_text='Select fields to search in. If none selected, search in all fields.')

    has_attribute = forms.MultipleChoiceField(label='Has Attribute', choices=[
        ('is_ignored', 'Ignored'),
        ('is_parked', 'Parked'),
        ('is_reserved', 'Reserved'),
        ('status_open', 'Open'),
        ('status_needs_tk_work', 'Needs TK Work'),
        ('status_irrelevant', 'Irrelevant'),
        ('status_reviewed', 'Reviewed')
    ], widget=Select2MultipleWidget(attrs={'data-placeholder': 'Attributes'}),
       required=False,
       help_text='Select attributes to search for. (OR logic)')

    sort_by = forms.ChoiceField(label='Sort', choices=[
        ('title', 'Document Title'),
        ('document_id', 'Transkribus Doc ID'),
        ('created_at', 'Created At'),
        ('updated_at', 'Updated At'),
        ('created_by', 'Created By'),
        ('updated_by', 'Updated By'),
    ], widget=Select2Widget(attrs={'data-placeholder': 'Sort by'}),
       required=False,
       help_text='Select field to sort by.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        helper = FormHelper()
        helper.form_method = 'post'
        helper.form_class = 'form form-control'

        helper.layout = Layout(
            Row(
                Column('search_term', css_class='form-group col-6 mb-3'),
                Column('search_in', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Row(
                Column('has_attribute', css_class='form-group col-6 mb-3'),
                Column('sort_by', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            ),
            Div(
                Submit('search', 'Search', css_class='btn btn-dark'),
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
