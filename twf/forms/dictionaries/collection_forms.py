from crispy_forms.layout import Row, Column
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

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start OpenAI Batch'


class CollectionGeminiBatchForm(CollectionBatchForm):
    """Form for batch processing Geonames data."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Gemini Batch'


class CollectionClaudeBatchForm(CollectionBatchForm):
    """Form for batch processing Geonames data."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Claude Batch'

