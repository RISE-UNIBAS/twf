"""Forms for the twf app."""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Column, Row, Div
from django_select2 import forms as s2forms
from jsoneditor.forms import JSONEditor

from twf.models import DictionaryEntry, Dictionary


class DictionaryForm(forms.ModelForm):
    """Form for creating and updating a dictionary."""

    class Meta:
        model = Dictionary
        fields = ['label', 'type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('label', css_class='form-group col-md-6 mb-0'),
                Column('type', css_class='form-group col-md-6 mb-0'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Save Dictionary', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


class DictionaryEntryForm(forms.ModelForm):
    """Form for creating and updating a dictionary entry."""

    class Meta:
        model = DictionaryEntry
        fields = ['label', 'notes', 'authorization_data']
        widgets = {
            'authorization_data': JSONEditor(attrs={
                'style': 'min-height: 400px;'  # Set your desired minimum height here
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('label', css_class='form-group col-md-6 mb-0'),
                Column('notes', css_class='form-group col-md-6 mb-0'),
                css_class='row form-row'
            ),
            Row(
                Column('authorization_data', css_class='form-group col-md-12 mb-0'),
            ),
            Div(
                Submit('delete_entry', 'Delete Dictionary Entry', css_class='btn btn-danger'),
                Submit('save_entry', 'Save Dictionary Entry', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


class CreateDictionaryEntryForm(forms.Form):
    """Form for creating a new dictionary entry."""

    label = forms.CharField(max_length=100, label='Label')
    notes = forms.CharField(widget=forms.Textarea(
        attrs={'rows': '3'}
    ), required=False, label='Notes')


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


class DictionaryImportForm(forms.Form):
    """Form for importing a dictionary."""

    type_selection = forms.ChoiceField(choices=(('csv','CSV'), ('json','JSON')), label='File Type')
    file = forms.FileField(label='Dictionary File')
    label = forms.CharField(max_length=100, label='Label')
    type = forms.CharField(label='Type')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('type_selection', css_class='form-group col-md-12 mb-0'),
                css_class='row form-row'
            ),
            Row(
                Column('file', css_class='form-group col-md-12 mb-0'),
                css_class='row form-row'
            ),
            Row(
                Column('label', css_class='form-group col-md-6 mb-0'),
                Column('type', css_class='form-group col-md-6 mb-0'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Import Dictionary', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )
