"""Forms for the twf app."""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Column, Row, Div

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
        fields = ['label', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('label', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            ),
            Row(
                Column('notes', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            ),
            Div(
                Submit('save_entry', 'Save Dictionary Entry', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


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
