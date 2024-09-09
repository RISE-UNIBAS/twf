from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Column, Div, Row
from django import forms


class ExportDataForm(forms.Form):
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('csv', 'CSV'),
        ('excel', 'Excel')
    ]

    export_type = forms.ChoiceField(choices=[], label='What to export')
    export_format = forms.ChoiceField(choices=FORMAT_CHOICES, label='Export Format')
    schema = forms.CharField(widget=forms.Textarea, required=False, label='Schema (Optional)',
                             help_text='Enter a JSON array of fields to include in the export')

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super().__init__(*args, **kwargs)

        et_choices = [
            ('documents', 'All Documents'),
        ]
        for col in project.collections.all():
            et_choices.append((f'collection_{col.id}', f'Collection: {col.title}'))

        self.fields['export_type'].choices = et_choices

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('export_type', css_class='form-group col-6 mb-0'),
                Column('export_format', css_class='form-group col-6 mb-0'),
                css_class='row form-row'
            ),
            Row(
                Column('schema', css_class='form-group col-12 mb-0'),
                css_class='row form-row'
            ),
            Div(
                Submit('submit', 'Start Batch', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )
