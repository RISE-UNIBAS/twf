from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Div, Button
from django import forms
from django_select2.forms import Select2Widget

from twf.forms.base_batch_forms import BaseBatchForm


class CollectionBatchForm(BaseBatchForm):
    """ Base form for batches of dictionaries. """

    collection = forms.ChoiceField(label='Collection', required=True,
                                   widget=Select2Widget(attrs={'style': 'width: 100%;'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['collection'].choices = ([('', 'Select a Collection')] +
                                             [(d.pk, d.title) for d in self.project.collections.all()])

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return [Row(
            Column('collection', css_class='form-group col-12 mb-0'),
            css_class='row form-row'
        )]


class CollectionOpenaiBatchForm(CollectionBatchForm):
    """Form for batch processing Geonames data."""

    prompt = forms.CharField(label='Prompt', required=True, widget=forms.Textarea,
                             help_text='The prompt for the OpenAI API. '
                                       'Use the token {label} to insert the entry label.')

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start OpenAI Batch'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        fields = super().get_dynamic_fields()
        fields.append(Row(
            Column('prompt', css_class='form-group col-12 mb-0'),
            css_class='row form-row'
        ))
        return fields
