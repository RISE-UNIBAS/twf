"""Forms for the twf app."""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Row, Column, HTML, Div, Button

from twf.models import Project


class BasicTaskForm(forms.Form):
    """Basic form for a task."""

    project = None

    progress_details = forms.CharField(label='Progress', required=False)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        self.fields['progress_details'].widget = forms.Textarea()
        self.fields['progress_details'].widget.attrs = {'readonly': True, 'rows': 5}

        progress_bar_html = """
        <div class="col-12 border text-center">
          <span>Progress:</span>
          <div class="progress">
            <div class="progress-bar bg-dark" role="progressbar" 
                 style="width: 0;" id="taskProgressBar" aria-valuenow="0" 
                 aria-valuemin="0" aria-valuemax="100">0%</div>
            </div>
        </div>"""

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        buttons = []
        if self.has_test_button():
            buttons.append(Button('testBatch', self.get_test_button_label(), css_class='btn btn-secondary'))
        buttons.append(Button('startBatch', self.get_button_label(), css_class='btn btn-dark'))

        self.helper.layout = Layout(
            *self.get_dynamic_fields(),
            HTML(progress_bar_html),
            Row(
                Column('progress_details', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            ),
            Div(
                *buttons,
                css_class='text-end pt-3'
            )
        )

    def has_test_button(self):
        """Return True if the form has a test button."""
        return False

    def get_button_label(self):
        """Return the label for the main button."""
        return 'Start Batch'

    def get_test_button_label(self):
        """Return the label for the test button."""
        return 'Test Batch'

    def get_dynamic_fields(self):
        """Return a list of dynamic fields. Needs to be implemented by subclasses."""
        return []


class WikidataSearchForm(forms.Form):
    """Form for searching Wikidata."""
    search_query = forms.CharField(label='Wikidata Sparql Query', widget=forms.Textarea(attrs={'rows': '5'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['search_query'].initial = ('SELECT ?item ?itemLabel ?itemDescription WHERE {\n'
                                               '  ?item wdt:P31 wd:Q5;  # instances of human\n'
                                               '        rdfs:label "__ENTRY__"@de.\n'
                                               '  SERVICE wikibase:label { bd:serviceParam wikibase:language "de". }\n'
                                               '}')

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('search_query', css_class='form-control'),
            Submit('submit', 'Save', css_class='btn btn-primary mt-2'))


class GeonamesSearchForm(forms.Form):
    """Form for searching Geonames."""
    search_query = forms.CharField(label='Search')
    username = forms.CharField(label='Username')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['search_query'].initial = '__ENTRY__'

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Field('search_query', css_class='form-control', wrapper_class='flex-fill'),
                Field('username', css_class='form-control', wrapper_class='flex-fill'),
                css_class='d-flex'
            ),
            Submit('submit', 'Save', css_class='btn btn-primary mt-2')
        )


class GNDSearchForm(forms.Form):
    """Form for searching the GND."""
    search_query = forms.CharField(label='Search')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['search_query'].initial = 'dnb.mat="persons" AND dnb.woe="__ENTRY__"'

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('search_query', css_class='form-control'),
            Submit('submit', 'Save', css_class='btn btn-primary mt-2'))
