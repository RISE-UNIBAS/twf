from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Div, Submit, Field
from django import forms

from twf.utils.date_utils import parse_date_string


class DateNormalizationForm(forms.Form):
    """Form for date normalization."""

    resolve_to = forms.ChoiceField(
        label='Resolve to',
        choices=[('year', 'Year'), ('month', 'Month'), ('day', 'Day')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Choose the level of resolution for the date normalization. For example, if the date is '2022', "
                  "the resolved date will be '2022-XX-XX' if you choose 'Day'."
    )

    input_date_format = forms.ChoiceField(
        label='Input Date Format',
        choices=[('DMY', 'Day-Month-Year'), ('MDY', 'Month-Day-Year'), ('YMD', 'Year-Month-Day')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="If you have ambiguous formats like '01/02/2022', '2022-02-01', etc., choose the appropriate format."
    )

    resulting_date = forms.CharField(
        label='Resulting Date',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="This is a proposal of the resulting date after normalization. "
    )

    date_tag = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        date_tag = kwargs.pop('date_tag', None)
        super().__init__(*args, **kwargs)

        if not project or not date_tag:
            raise ValueError("Project and date_tag are required.")

        conf = project.get_task_configuration("date_normalization")

        resolve_to = conf.get('resolve_to', 'day')
        input_date_format = conf.get('input_date_format', 'DMY')
        normalized_date = parse_date_string(date_tag.variation, resolve_to=resolve_to, date_format=input_date_format)

        self.fields['input_date_format'].initial = input_date_format
        self.fields['resolve_to'].initial = resolve_to
        self.fields['resulting_date'].initial = normalized_date
        self.fields['date_tag'].initial=date_tag.pk

        self.helper = FormHelper()
        self.helper.method = 'post'

        self.helper.layout = Layout()

        input_string_html = f"""
        <div class="col-12 border text-center">
            <p class="text-center" style="color: #7c7c7c">Try to normalize:
                <a href="{{% url 'twf:tags_park' {date_tag.pk} %}}" class="btn btn-secondary float-end">Park</a>
            </p>
            <p class="display-6 text-center">{ date_tag.variation }</p>
        </div>"""

        self.helper.layout.append(
            Field('date_tag', type="hidden")  # Ensures `date_tag` is included in the form as a hidden input
        )

        self.helper.layout.append(
            Row(
                Column('input_date_format', css_class='form-group col-6 mb-3'),
                Column('resolve_to', css_class='form-group col-6 mb-3'),
                css_class='row form-row'
            )
        )

        self.helper.layout.append(
            Row(
                HTML(input_string_html),
                css_class='row form-row'
            )
        )

        self.helper.layout.append(
            Row(
                Column('resulting_date', css_class='form-group col-12 mb-3'),
                css_class='row form-row'
            )
        )

        self.helper.layout.append(
            Div(
                Submit('submit', 'Accept & Next', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            )
        )
