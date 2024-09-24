from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Div, HTML
from django import forms

from twf.forms.forms import BasicTaskForm
from twf.models import Document


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


class BatchOpenAIForm(BasicTaskForm):

    role_description = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        'placeholder': 'Describe the role here...'
    }), label="Role Description")

    prompt = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Enter your prompt here...'
    }), label="Prompt")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Run Project Batch'

    def get_test_button_label(self):
        return 'Test One Document'

    def has_test_button(self):
        return True

    def get_dynamic_fields(self):
        return [
            Row(
                Column('role_description', css_class='form-group'),
                css_class='row form-row'
            ),
            Row(
                Column('prompt', css_class='form-group'),
                css_class='row form-row'
            ),
        ]

