"""Forms for enriching dictionary entries"""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Row, Column, Layout, Div, Submit, HTML, Button
from django import forms

from twf.models import Dictionary


class LoadMetadataForm(forms.Form):
    """Form for loading metadata from a CSV file."""

    data_target_type = forms.ChoiceField(
        label='Data Target Type',
        choices=[('document', 'Document'), ('page', 'Page')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    data_file = forms.FileField(
        label='Data File',
        required=True
    )

    json_data_key = forms.CharField(
        label='JSON Data Key',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    match_to_field = forms.ChoiceField(
        label='Match to Field',
        choices=[('dbid', 'Database ID'),
                 ('docid', 'Transkribus Document/Page ID')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.method = 'post'

        self.helper.layout = Layout()

        self.helper.layout.append(
            Row(
                Column('data_target_type', css_class='form-group col-6 mb-3'),
                Column('data_file', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            )
        )
        self.helper.layout.append(
            Row(
                Column('json_data_key', css_class='form-group col-6 mb-3'),
                Column('match_to_field', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            )
        )
        self.helper.layout.append(
            Div(
                Submit('submit', 'Load Data', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


class ExtractMetadataValuesForm(forms.Form):
    """Form for extracting metadata values from a JSON file
    and associating them with dictionary entries."""

    json_data_key = forms.CharField(
        label='JSON Data Key',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    dictionary = forms.ModelChoiceField(
        label='Dictionary',
        queryset=Dictionary.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        self.fields['dictionary'].queryset = project.selected_dictionaries.all()

        self.helper = FormHelper()
        self.helper.method = 'post'

        self.helper.layout = Layout()

        self.helper.layout.append(
            Row(
                Column('json_data_key', css_class='form-group col-6 mb-3'),
                Column('dictionary', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            )
        )

        self.helper.layout.append(
            Div(
                Submit('submit', 'Load Data', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )


class LoadSheetsMetadataForm(forms.Form):
    """ Form for loading metadata from Google Sheets. """

    project = None
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

        self.fields['progress_details'].widget = forms.Textarea()
        self.fields['progress_details'].widget.attrs = {'readonly': True, 'rows': 5}

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            HTML(progress_bar_html),
            Row(
                Column('progress_details', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            ),
            Div(
                Button('startBatch', 'Load Sheets Metadata', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )
