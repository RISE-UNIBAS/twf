"""Filter classes for the twf app."""
import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Field, Submit
from django.forms import CheckboxInput

from .models import Document, DictionaryEntry, PageTag


class TagFilter(django_filters.FilterSet):
    """Filter for the tags table."""

    variation_type = django_filters.ChoiceFilter(
        field_name='variation_type',
        label='Variation Type',
        choices=[],  # Placeholder for choices, will populate dynamically
    )

    class Meta:
        """Meta class for the tag filter."""
        model = PageTag
        fields = {
            'variation': ['icontains'],
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        excluded = kwargs.pop('excluded', [])

        super().__init__(*args, **kwargs)

        # Dynamically populate the choices for variation_type
        distinct_variation_types = (
            PageTag.objects.filter(page__document__project=project)
            .exclude(variation_type__in=excluded)
            .distinct()
            .values('variation_type')
            .order_by('variation_type')
        )

        choices = [(vt['variation_type'], vt['variation_type']) for vt in distinct_variation_types]
        # print(choices)
        self.filters['variation_type'].extra.update({
            'choices': choices
        })


class DocumentFilter(django_filters.FilterSet):
    """Filter for the documents table."""

    is_parked = django_filters.BooleanFilter(
        label="Ignored",
        widget=CheckboxInput()
    )

    class Meta:
        model = Document
        fields = {
            'document_id': ['icontains'],
            'title': ['icontains'],
            'is_parked': ['exact'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.helper = FormHelper()
        self.form.helper.form_method = 'get'
        self.form.helper.form_class = 'inline-form d-flex align-items-center'

        self.form.helper.layout = Layout(
            Row(
                Field('document_id__icontains', css_class='form-control', wrapper_class='col-4'),
                Field('title__icontains', css_class='form-control', wrapper_class='col-4'),
                Field('is_parked', wrapper_class='col-2'),
                Submit('submit', 'Filter', css_class='btn btn-primary col-2'),
            )
        )

class DictionaryEntryFilter(django_filters.FilterSet):
    """Filter for the dictionary entry table."""

    class Meta:
        """Meta class for the dictionary entry filter."""
        model = DictionaryEntry
        fields = {
            'label': ['icontains'],
        }
