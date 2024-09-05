"""Contains all forms concerning batch processes."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Submit
from django import forms

from twf.models import Dictionary


class GeonamesBatchForm(forms.Form):
    dictionary = forms.ChoiceField(label='Dictionary', required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dictionary'].choices = [(d.pk, d.label) for d in self.get_dictionaries()]

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('dictionary', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Start Batch', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )

    def get_dictionaries(self):
        return Dictionary.objects.all()
