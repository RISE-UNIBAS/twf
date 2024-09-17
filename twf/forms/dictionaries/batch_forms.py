"""Contains all forms concerning batch processes."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Div, Submit, HTML, Button
from django import forms


class DictionaryBatchForm(forms.Form):
    """ Base form for batches of dictionaries. """

    project = None
    dictionary = forms.ChoiceField(label='Dictionary', required=True)
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

        self.fields['dictionary'].choices = [(d.pk, d.label) for d in self.project.selected_dictionaries.all()]
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
                Button('startBatch', self.get_button_label(), css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )

    def get_button_label(self):
        return 'Start Batch'

    def get_dynamic_fields(self):
        return []


class GeonamesBatchForm(DictionaryBatchForm):
    """Form for batch processing Geonames data."""

    exactly_one = forms.BooleanField(label='Exactly One', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_button_label(self):
        return 'Start Geonames Batch'

    def get_dynamic_fields(self):
        fields = []
        fields.append(Row(
            Column('exatctly_one', css_class='form-group col-12 mb-0'),
            css_class='row form-row'
        ))
        return fields


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