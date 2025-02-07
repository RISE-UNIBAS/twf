"""Forms for the twf app."""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Row


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
