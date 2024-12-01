"""Contains all forms concerning batch processes."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Submit
from django import forms
from django_select2.forms import Select2Widget


class DictionaryRequestForm(forms.Form):
    """ Base form for batches of dictionaries. """

    project = None
    dictionary = forms.ChoiceField(label='Dictionary', required=True,
                                   widget= Select2Widget(attrs={'style': 'width: 100%;'}))

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if self.project is None:
            raise ValueError('Project must be provided.')

        self.fields['dictionary'].choices = [(d.pk, d.label) for d in self.project.selected_dictionaries.all()]
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('dictionary', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            ),
            # here comes a list of fields from an abstract method
            *self.get_dynamic_fields(),
            Div(
                Submit('submit', 'Start Batch', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return []


class GeonamesRequestForm(DictionaryRequestForm):
    """Form for batch processing Geonames data."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Geonames Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return []


class GNDRequestForm(DictionaryRequestForm):
    """Form for batch processing Geonames data."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start GND Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return []


class WikidataRequestForm(DictionaryRequestForm):
    """Form for batch processing Geonames data."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Wikidata Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return []


class OpenaiRequestForm(DictionaryRequestForm):
    """Form for batch processing Geonames data."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start OpenAI Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return []
