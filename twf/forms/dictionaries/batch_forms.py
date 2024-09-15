"""Contains all forms concerning batch processes."""
from abc import ABC, abstractmethod

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Submit
from django import forms

from twf.models import Dictionary


class DictionaryBatchForm(forms.Form, ABC):
    """ Base form for batches of dictionaries. """

    project = None
    dictionary = forms.ChoiceField(label='Dictionary', required=True)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if self.project is None:
            raise ValueError('Project must be provided.')

        self.fields['dictionary'].choices = [(d.pk, d.label) for d in self.project.dictionaries.all()]
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

    @abstractmethod
    def get_button_label(self):
        return 'Start Batch'

    @abstractmethod
    def get_dynamic_fields(self):
        return []


class GeonamesBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Start Geonames Batch'

    def get_dynamic_fields(self):
        return []


class GNDBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Start GND Batch'

    def get_dynamic_fields(self):
        return []


class WikidataBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Start Wikidata Batch'

    def get_dynamic_fields(self):
        return []


class OpenaiBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Start OpenAI Batch'

    def get_dynamic_fields(self):
        return []