"""Contains all forms concerning batch processes."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div,  HTML, Button
from django import forms
from django_select2.forms import Select2Widget


class DictionaryBatchForm(forms.Form):
    """ Base form for batches of dictionaries. """

    project = None
    dictionary = forms.ChoiceField(label='Dictionary', required=True,
                                   widget=Select2Widget(attrs={'style': 'width: 100%;'}))
    progress_details = forms.CharField(label='Progress', required=False)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if self.project is None:
            raise ValueError('Project must be provided.')

        progress_bar_html = """
        <div class="col-12 border text-center">
          <span>Progress:</span>
          <div class="progress">
            <div class="progress-bar bg-dark" role="progressbar" 
                 style="width: 0;" id="taskProgressBar" aria-valuenow="0" 
                 aria-valuemin="0" aria-valuemax="100">0%</div>
            </div>
        </div>"""

        self.fields['dictionary'].choices = ([('', 'Select a dictionary')] +
                                             [(d.pk, d.label) for d in self.project.selected_dictionaries.all()])
        self.fields['progress_details'].widget = forms.Textarea()
        self.fields['progress_details'].widget.attrs = {'readonly': True, 'rows': 5}

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Row(
                Column('dictionary', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            ),
            *self.get_dynamic_fields(),
            HTML(progress_bar_html),
            Row(
                Column('progress_details', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            ),
            Div(
                Button('startBatch', self.get_button_label(), css_class='btn btn-dark show-confirm-modal',
                              data_message=self.get_button_data_message()),
                css_class='text-end pt-3'
            )
        )

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Batch'

    def get_button_data_message(self):
        """Get the data message for the submit button."""
        return 'Are you sure you want to start the batch process?'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return []


class GeonamesBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    only_search_in = forms.CharField(label='Only search in', required=False,
                                     help_text='Enter a country code (ISO-3166) to only search in that country.'
                                               'Leave empty to search in all countries.')
    similarity_threshold = forms.IntegerField(label='Similarity threshold', required=False,
                                              help_text='The similarity threshold for the search results. '
                                                        'Default is 80.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['similarity_threshold'].initial = 80

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Geonames Batch'

    def get_button_data_message(self):
        """Get the data message for the submit button."""
        return 'Are you sure you want to start the Geonames batch process?'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        fields = []
        fields.append(Row(
            Column('only_search_in', css_class='form-group col-6 mb-0'),
            Column('similarity_threshold', css_class='form-group col-6 mb-0'),
            css_class='row form-row'
        ))
        return fields


class GNDBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    def get_button_label(self):
        return 'Start GND Batch'

    def get_button_data_message(self):
        """Get the data message for the submit button."""
        return 'Are you sure you want to start the GND batch process?'

    def get_dynamic_fields(self):
        return []


class WikidataBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    entity_type = forms.ChoiceField(label='Entity Type', required=True,
                                    choices=[('city', 'City'), ('person', 'Person'), ('event', 'Event'),
                                             ('ship', 'Ship'), ('building', 'Building')],
                                    widget=Select2Widget(attrs={'style': 'width: 100%;'}))
    language = forms.CharField(label='Language', required=True, initial='en')

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start Wikidata Batch'

    def get_button_data_message(self):
        """Get the data message for the submit button."""
        return 'Are you sure you want to start the Wikidata batch process?'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        fields = []
        fields.append(Row(
            Column('entity_type', css_class='form-group col-6 mb-0'),
            Column('language', css_class='form-group col-6 mb-0'),
            css_class='row form-row'
        ))
        return fields


class OpenaiBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    def get_button_label(self):
        """Get the label for the submit button."""
        return 'Start OpenAI Batch'

    def get_button_data_message(self):
        """Get the data message for the submit button."""
        return 'Are you sure you want to start the OpenAI batch process?'

    def get_dynamic_fields(self):
        """Get the dynamic fields for the form."""
        return []
