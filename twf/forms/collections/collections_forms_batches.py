from crispy_forms.layout import Row, Column
from django import forms

from twf.forms.base_batch_forms import BaseAIBatchForm
from twf.models import Collection


class CollectionBatchForm(BaseAIBatchForm):
    """Form for batch processing Geonames data."""

    collection = forms.ModelChoiceField(
        queryset=Collection.objects.none(),
        label='Collection',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['collection'].choices = ([('', 'Select a Collection')] +
                                             [(c.pk, c.title) for c in Collection.objects.filter(project=self.project)])


    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return super().get_dynamic_fields() + [Row(
            Column('collection', css_class='form-group col-12 mb-3'),
            css_class='row form-row'
        )]

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Batch'


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

