"""Forms for the twf app."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from django_select2 import forms as s2forms

from twf.models import Project, DictionaryEntry


class LoginForm(AuthenticationForm):
    """Form for logging in users."""

    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'username',
            'password',
            Submit('submit', 'Login', css_class='btn btn-success')
        )


class CreateDictionaryEntryForm(forms.Form):
    """Form for creating a new dictionary entry."""

    label = forms.CharField(max_length=100, label='Label')
    notes = forms.CharField(widget=forms.Textarea, required=False, label='Notes')


class AssignToEntryForm(forms.Form):
    """Form for assigning a tag to a dictionary entry."""
    entry = forms.ChoiceField(
        label="Select Dictionary Entry",
        widget=s2forms.Select2Widget
    )

    def __init__(self, *args, **kwargs):
        tag_type = kwargs.pop('tag_type')
        super().__init__(*args, **kwargs)
        self.fields['entry'].choices = DictionaryEntry.objects.filter(
            dictionary__type=tag_type).values_list('id', 'label')


class GoogleDocsSettingsForm(forms.ModelForm):
    """Form for the Google Docs settings."""

    metadata_google_valid_columns = forms.CharField(widget=forms.Textarea(attrs={'rows':'2'}), required=False)

    class Meta:
        model = Project
        fields = ['metadata_google_sheet_id', 'metadata_google_sheet_range', 'metadata_google_doc_id_column',
                  'metadata_google_title_column', 'metadata_google_valid_columns']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('metadata_google_sheet_id', css_class='form-control'),
            Field('metadata_google_sheet_range', css_class='form-control'),
            Field('metadata_google_doc_id_column', css_class='form-control'),
            Field('metadata_google_title_column', css_class='form-control'),
            Field('metadata_google_valid_columns', css_class='form-control'),
            Submit('submit', 'Save', css_class='btn btn-primary mt-2')
        )
