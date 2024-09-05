from datetime import datetime

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Row, Column, HTML, Div
from django import forms
from django.core.exceptions import ValidationError
from django_select2.forms import Select2Widget

from twf.models import Dictionary


def parse_config(json_config, json_data):
    """Parse JSON configuration and return form fields."""
    form_fields = []
    for field_name, field_config in json_config.items():
        field_value = json_data.get(field_name, '')
        field_config['name'] = field_name
        field_config['value'] = field_value
        form_fields.append(field_config)
    return form_fields


class DynamicForm(forms.Form):
    """Dynamic form based on JSON configuration."""
    def __init__(self, *args, **kwargs):
        json_config = kwargs.pop('json_config', None)
        json_data = kwargs.pop('json_data', None)
        super(DynamicForm, self).__init__(*args, **kwargs)

        form_field_config = parse_config(json_config, json_data)
        # print(form_field_config)

        self.helper = FormHelper()
        self.helper.form_id = 'review-form'
        self.helper.form_method = 'post'
        self.helper.layout = Layout()

        for field in form_field_config:
            field_name = field.get('name', '')
            field_type = field.get('type', 'text')
            field_label = field.get('label', field_name)
            field_value = field.get('value', '')
            field_required = field.get('required', False)
            extra_html = ''

            if field_type == 'text':
                self.fields[field_name] = forms.CharField(label=field_label, initial=field_value,
                                                          required=field_required)
            elif field_type == 'textarea':
                self.fields[field_name] = forms.CharField(label=field_label, initial=field_value,
                                                          widget=forms.Textarea, required=field_required)
            elif field_type == 'number':
                self.fields[field_name] = forms.IntegerField(label=field_label, initial=field_value,
                                                             required=field_required)
            elif field_type == 'checkbox':
                self.fields[field_name] = forms.BooleanField(label=field_label, initial=field_value,
                                                             required=field_required)
            elif field_type == 'select':
                extra_html = "Original value: " + field_value + "<br>"
                if "dictionary" in field:
                    dictionary_id = field.get('dictionary', None)
                    try:
                        dictionary = Dictionary.objects.get(pk=dictionary_id)
                        choices = [(item.id, item.label) for item in dictionary.entries.all()]
                    except Dictionary.DoesNotExist:
                        choices = []
                else:
                    choices = []
                self.fields[field_name] = forms.ChoiceField(label=field_label, choices=choices, initial=field_value,
                                                            required=field_required,
                                                            widget=Select2Widget(attrs={'style': 'width: 100%;'}))
            elif field_type == 'radio':
                choices = field.get('choices', [])
                self.fields[field_name] = forms.ChoiceField(label=field_label, choices=choices, initial=field_value,
                                                            widget=forms.RadioSelect, required=field_required)
            elif field_type == 'date':
                self.fields[field_name] = forms.CharField(label=field_label, initial=field_value,
                                                          required=field_required)
            elif field_type == 'time':
                self.fields[field_name] = forms.TimeField(label=field_label, initial=field_value,
                                                          required=field_required)
            elif field_type == 'datetime':
                self.fields[field_name] = forms.DateTimeField(label=field_label, initial=field_value,
                                                              required=field_required)

            validation_html = ''
            if 'validation' in field:
                self.fields[field_name].validators.append(
                    self.get_validator(field)
                )
                validation_html = f'<span id="{field_name}-feedback" class="validation-feedback"></span>'

            extra_outer_html = f'<div class="border h-100">{validation_html}{extra_html}</div>'

            row_to_append = Row(
                Column(field_name, css_class='form-group col-8 mb-3'),
                Column(HTML(extra_outer_html), css_class='form-group col-4 mb-3'),
                css_class='row form-row'
            )
            self.helper.layout.append(row_to_append)

        self.helper.layout.append(Div(
                Submit('submit', 'Save And Next', css_class='btn btn-dark'),
                css_class='text-end pt-3'
            ))
        self.is_valid()

    def get_validator(self, validation_conf):
        """Return a validator function based on the validation configuration."""

        def validate(value):
            # Implement your validation logic based on the validation_conf
            if not self.validation_logic(value, validation_conf):
                raise ValidationError('Invalid value')
        return validate

    @staticmethod
    def validation_logic(value, field_conf):
        """Implement custom validation logic based on the field configuration"""
        validation_conf = field_conf.get("validation", {})
        field_type = field_conf["type"]

        # DATES
        if field_type == "date":
            date_format = validation_conf.get("format", "%Y-%m-%d")
            print("DATE FORMAT", value, date_format)
            try:
                datetime.strptime(value, date_format)
                return True
            except ValueError:
                return False
        # NUMBERS
        elif field_type == "number":
            return True

        return True  # Replace with actual validation logic


def flatten_json(nested_json, parent_key='', sep='_'):
    """
    Flatten a nested JSON object.
    :param nested_json: The JSON object to flatten.
    :param parent_key: The base key string for nested elements.
    :param sep: The separator between keys.
    :return: A flat dictionary.
    """
    items = []
    for k, v in nested_json.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
