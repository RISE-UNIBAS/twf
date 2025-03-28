"""Filter classes for the twf app."""
import logging
import django_filters
from django.forms import CheckboxInput
from django.contrib.auth import get_user_model
from twf.models import Document, DictionaryEntry, PageTag, CollectionItem, Task, Prompt, Project, Export, Note

User = get_user_model()

logger = logging.getLogger(__name__)


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
        logger.debug("Tag variation type filter choices: %s", choices)
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
        """Meta class for the document filter."""
        model = Document
        fields = {
            'document_id': ['icontains'],
            'title': ['icontains'],
            'is_parked': ['exact'],
        }


class TaskFilter(django_filters.FilterSet):
    """Filter for the tasks table."""

    class Meta:
        """Meta class for the task filter."""
        model = Task
        fields = {
            'status': ['icontains'],
        }

class PromptFilter(django_filters.FilterSet):
    """Filter for the prompts table."""

    class Meta:
        """Meta class for the prompt filter."""
        model = Prompt
        fields = {
            'system_role': ['icontains'],
        }


class NoteFilter(django_filters.FilterSet):
    """Filter for the prompts table."""

    class Meta:
        """Meta class for the prompt filter."""
        model = Note
        fields = {
            'note': ['icontains'],
        }

class ProjectFilter(django_filters.FilterSet):
    """Filter for the projects table."""

    title = django_filters.CharFilter(lookup_expr='icontains', label="Title contains")
    status = django_filters.ChoiceFilter(choices=Project.STATUS_CHOICES)
    owner__user__username = django_filters.CharFilter(lookup_expr='icontains', label="Owner username")

    class Meta:
        model = Project
        fields = ['title', 'status', 'owner__user__username']


class DictionaryEntryFilter(django_filters.FilterSet):
    """Filter for the dictionary entry table."""

    class Meta:
        """Meta class for the dictionary entry filter."""
        model = DictionaryEntry
        fields = {
            'label': ['icontains'],
        }



class CollectionItemFilter(django_filters.FilterSet):
    """Filter for the collection item table."""

    document_id = django_filters.CharFilter(field_name="document__document_id", lookup_expr="icontains",
                                            label="Document ID")
    title = django_filters.CharFilter(lookup_expr='icontains', label="Item Title")
    document_title = django_filters.CharFilter(field_name="document__title", lookup_expr="icontains",
                                               label="Document Title")

    class Meta:
        """Meta class for the collection item filter."""
        model = CollectionItem
        fields = ["document_id", "title", "document_title"]


class UserFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(lookup_expr="icontains", label="Username contains")
    email = django_filters.CharFilter(lookup_expr="icontains", label="Email contains")
    is_active = django_filters.BooleanFilter(label="Is Active")
    is_superuser = django_filters.BooleanFilter(label="Is Admin")

    class Meta:
        model = User
        fields = ["username", "email", "is_active", "is_superuser"]


class ExportFilter(django_filters.FilterSet):
    export_type = django_filters.CharFilter(lookup_expr='icontains', label="Type")
    created_by__username = django_filters.CharFilter(lookup_expr='icontains', label="Created by")
    created = django_filters.DateFromToRangeFilter(label="Created between")

    class Meta:
        model = Export
        fields = ["export_type", "created_by__username", "created"]