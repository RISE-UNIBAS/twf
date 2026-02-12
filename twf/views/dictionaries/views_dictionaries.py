"""Views for the dictionary overview and the dictionary entries."""

import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

logger = logging.getLogger(__name__)

from twf.forms.filters.filters import DictionaryEntryFilter, DictionaryFilter
from twf.forms.dictionaries.dictionaries_forms import (
    DictionaryForm,
    DictionaryEntryForm,
)
from twf.forms.enrich_forms import EnrichEntryManualForm, EnrichEntryForm
from twf.forms.tags.enrichment_forms import get_enrichment_form_class
from twf.models import Dictionary, DictionaryEntry, Variation, PageTag, Workflow
from twf.utils.project_statistics import get_dictionary_statistics
from twf.workflows.dictionary_workflows import create_dictionary_enrichment_workflow
from twf.tables.tables_dictionary import (
    DictionaryTable,
    DictionaryEntryTable,
    DictionaryEntryVariationTable,
    DictionaryAddTable,
)
from twf.views.views_base import TWFView


class TWFDictionaryView(LoginRequiredMixin, TWFView):
    """Base view for all dictionary views."""

    template_name = None

    def get_sub_navigation(self):
        """Get the sub navigation."""
        sub_nav = [
            {
                "name": "Dictionaries Options",
                "options": [
                    {"url": reverse("twf:dictionaries_overview"), "value": "Overview"},
                    {
                        "url": reverse("twf:dictionaries"),
                        "value": "Dictionaries",
                        "permission": "dictionary.view",
                    },
                    {
                        "url": reverse("twf:dictionaries_add"),
                        "value": "Add Dictionaries",
                        "permission": "dictionary.manage",
                    },
                    {
                        "url": reverse("twf:dictionary_create"),
                        "value": "Create New Dictionary",
                        "permission": "dictionary.manage",
                    },
                ],
            },
            {
                "name": "Automated Workflows",
                "options": self.get_ai_batch_options()
                + [
                    {
                        "url": reverse("twf:dictionaries_batch_gnd"),
                        "value": "GND",
                        "permission": "dictionary.manage",
                    },
                    {
                        "url": reverse("twf:dictionaries_batch_wikidata"),
                        "value": "Wikidata",
                        "permission": "dictionary.manage",
                    },
                    {
                        "url": reverse("twf:dictionaries_batch_geonames"),
                        "value": "Geonames",
                        "permission": "dictionary.manage",
                    },
                ],
            },
            {
                "name": "Supervised Workflows",
                "options": self.get_ai_request_options()
                + [
                    {
                        "url": reverse("twf:dictionaries_request_gnd"),
                        "value": "GND",
                        "permission": "dictionary.edit",
                    },
                    {
                        "url": reverse("twf:dictionaries_request_wikidata"),
                        "value": "Wikidata",
                        "permission": "dictionary.edit",
                    },
                    {
                        "url": reverse("twf:dictionaries_request_geonames"),
                        "value": "Geonames",
                        "permission": "dictionary.edit",
                    },
                ],
            },
            {
                "name": "Manual Workflows",
                "options": [
                    {
                        "url": reverse("twf:dictionaries_normalization"),
                        "value": "Manual Assignment",
                        "permission": "dictionary.edit",
                    },
                    {
                        "url": reverse("twf:dictionaries_entry_merging"),
                        "value": "Merge Entries",
                        "permission": "dictionary.edit",
                    },
                ],
            },
        ]
        return sub_nav

    def get_navigation_index(self):
        """Get the navigation index."""
        return 5

    def get_ai_batch_options(self):
        """
        Get the AI batch options.
        Returns simplified navigation with unified AI Batch processing.
        """
        options = [
            {
                "url": reverse("twf:dictionaries_batch_ai_unified"),
                "value": "AI Batch Processing",
                "permission": "dictionary.manage",
            }
        ]
        return options

    def get_ai_request_options(self):
        """
        Get the AI request options.
        Returns simplified navigation with unified AI Request processing.
        """
        options = [
            {
                "url": reverse("twf:dictionaries_request_ai_unified"),
                "value": "AI Request",
                "permission": "dictionary.edit",
            }
        ]
        return options

    def get_dictionaries(self):
        """Get the dictionaries."""
        project = self.get_project()
        return project.selected_dictionaries.all()

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        return context

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.page_title is None:
            self.page_title = kwargs.get("page_title", "Dictionary View")


class TWFDictionaryOverviewView(TWFDictionaryView):
    """View for the dictionary overview."""

    template_name = "twf/dictionaries/overview.html"
    page_title = "Dictionaries"
    show_context_help = False

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        context["dict_stats"] = get_dictionary_statistics(project)
        return context


class TWFDictionaryDictionariesView(SingleTableView, FilterView, TWFDictionaryView):
    """View for the dictionaries. Provides a table of all dictionaries.
    The table is filterable and sortable."""

    template_name = "twf/dictionaries/dictionaries.html"
    page_title = "Dictionaries Overview"
    table_class = DictionaryTable
    filterset_class = DictionaryFilter
    paginate_by = 10
    model = Dictionary
    strict = False  # Don't enforce form validation for filters

    def get_queryset(self):
        """Get the queryset."""
        project = self.get_project()
        queryset = project.selected_dictionaries.all()
        self.filterset = self.filterset_class(
            self.request.GET or None, queryset=queryset
        )

        # If filter is applied, return filtered queryset
        if self.request.GET and self.filterset.is_bound:
            return self.filterset.qs
        return queryset

    def get(self, request, *args, **kwargs):
        """Handle the GET request with proper filter handling."""
        # Set up initial queryset
        project = self.get_project()
        queryset = project.selected_dictionaries.all()

        # Initialize the filter
        self.filterset = self.filterset_class(request.GET or None, queryset=queryset)

        # Set object_list either to all items or filtered items
        if request.GET and self.filterset.is_bound:
            self.object_list = self.filterset.qs
        else:
            self.object_list = queryset

        # Get context and render response
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class TWFDictionaryAddView(SingleTableView, FilterView, TWFDictionaryView):
    """View for adding dictionaries to the project."""

    template_name = "twf/dictionaries/dictionaries_add.html"
    page_title = "Add Dictionaries"
    table_class = DictionaryAddTable
    filterset_class = DictionaryFilter
    paginate_by = 10
    model = Dictionary
    strict = False  # Don't enforce form validation for filters

    def get_queryset(self):
        """Get the queryset of dictionaries not already in the project."""
        project = self.get_project()

        # Get the IDs of dictionaries already in the project more efficiently
        selected_dictionary_ids = project.selected_dictionaries.values_list(
            "id", flat=True
        )

        # Get all dictionaries except those already in the project
        queryset = Dictionary.objects.exclude(id__in=selected_dictionary_ids)

        # Initialize the filter
        self.filterset = self.filterset_class(
            self.request.GET or None, queryset=queryset
        )

        # If filter is applied, return filtered queryset
        if self.request.GET and self.filterset.is_bound:
            return self.filterset.qs
        return queryset

    def get(self, request, *args, **kwargs):
        """Handle the GET request with proper filter handling."""
        # Get the queryset using the existing method to avoid code duplication
        queryset = self.get_queryset()

        # Set object_list to the queryset
        self.object_list = queryset

        # Log the count for debugging
        logger.debug(f"Available dictionaries count: {queryset.count()}")

        # Get context and render response
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


class TWFDictionaryCreateView(FormView, TWFDictionaryView):
    """Create a new dictionary."""

    template_name = "twf/dictionaries/create.html"
    form_class = DictionaryForm
    success_url = reverse_lazy("twf:dictionaries")

    def form_valid(self, form):
        """Handle the form submission."""
        # Save the form
        form.instance.save(current_user=self.request.user)
        project = self.get_project()
        project.selected_dictionaries.add(form.instance)
        project.save()

        # Add a success message
        messages.success(
            self.request,
            "Dictionary has been created successfully and has been added to your project.",
        )

        # Redirect to the success URL
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Create New Dictionary"
        return context


class TWFDictionaryDictionaryView(SingleTableView, FilterView, TWFDictionaryView):
    """View for the dictionary entries. Provides a table of dictionary entries of a single dictionary.
    The table is filterable and sortable."""

    template_name = "twf/dictionaries/dictionary.html"
    page_title = "View Dictionary"
    navigation_anchor = reverse_lazy("twf:dictionaries")

    table_class = DictionaryEntryTable
    filterset_class = DictionaryEntryFilter
    paginate_by = 10
    model = DictionaryEntry
    strict = False  # Don't enforce form validation for filters

    def get_queryset(self):
        """Get the queryset."""
        queryset = DictionaryEntry.objects.filter(dictionary_id=self.kwargs.get("pk"))
        self.filterset = self.filterset_class(
            self.request.GET or None, queryset=queryset
        )

        # If filter is applied, return filtered queryset
        if self.request.GET and self.filterset.is_bound:
            return self.filterset.qs
        return queryset

    def get(self, request, *args, **kwargs):
        """Handle the GET request with proper filter handling."""
        # Set up initial queryset
        queryset = DictionaryEntry.objects.filter(dictionary_id=self.kwargs.get("pk"))

        # Initialize the filter
        self.filterset = self.filterset_class(request.GET or None, queryset=queryset)

        # Set object_list either to all items or filtered items
        if request.GET and self.filterset.is_bound:
            self.object_list = self.filterset.qs
        else:
            self.object_list = queryset

        # Get context and render response
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context["dictionary"] = Dictionary.objects.get(pk=self.kwargs.get("pk"))
        context["filter"] = self.filterset
        return context

    def get_breadcrumbs(self):
        """Get the breadcrumbs for dictionary entry view."""
        # Start with home and dictionaries section
        breadcrumbs = [
            {"url": reverse("twf:home"), "value": '<i class="fas fa-home"></i>'},
            {"url": reverse("twf:dictionaries"), "value": "Dictionaries"},
        ]

        # Get the entry and its dictionary
        dictionary = Dictionary.objects.get(pk=self.kwargs.get("pk"))
        breadcrumbs.append(
            {
                "url": reverse("twf:dictionaries_view", args=[dictionary.pk]),
                "value": dictionary.label,
            }
        )
        return breadcrumbs


class TWFDictionaryDictionaryEntryView(SingleTableView, TWFDictionaryView):
    """View for a single dictionary entry."""

    template_name = "twf/dictionaries/dictionary_entry.html"
    page_title = "View Dictionary Entry"
    table_class = DictionaryEntryVariationTable
    navigation_anchor = reverse_lazy("twf:dictionaries")

    def get_queryset(self):
        """Get the queryset."""
        return Variation.objects.filter(entry_id=self.kwargs.get("pk"))

    def get(self, request, *args, **kwargs):
        """Handle the GET request."""
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_breadcrumbs(self):
        """Get the breadcrumbs for dictionary entry view."""
        # Start with home and dictionaries section
        breadcrumbs = [
            {"url": reverse("twf:home"), "value": '<i class="fas fa-home"></i>'},
            {"url": reverse("twf:dictionaries_overview"), "value": "Dictionaries"},
            {"url": reverse("twf:dictionaries"), "value": "Dictionary List"},
        ]

        # Get the entry and its dictionary
        entry = self.get_entry()
        if entry:
            # Add the dictionary to the breadcrumbs
            breadcrumbs.append(
                {
                    "url": reverse("twf:dictionaries_view", args=[entry.dictionary.pk]),
                    "value": entry.dictionary.label,
                }
            )

            # Add the entry itself
            breadcrumbs.append(
                {"url": self.request.path, "value": f"Entry: {entry.label}"}
            )

        return breadcrumbs

    def get_entry(self):
        """Get the dictionary entry."""
        try:
            return DictionaryEntry.objects.get(pk=self.kwargs.get("pk"))
        except DictionaryEntry.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        table = self.table_class(self.object_list, project=self.get_project())
        context["table"] = table

        entry = self.get_entry()
        context["entry"] = entry

        # Check if entry has enrichment data
        if entry and entry.metadata:
            # Filter enrichment data (keys that have normalized_value and enrichment_data structure)
            enrichment_data = {}
            for key, value in entry.metadata.items():
                if isinstance(value, dict) and "normalized_value" in value and "enrichment_data" in value:
                    enrichment_data[key] = value

            context["has_enrichment"] = bool(enrichment_data)
            context["enrichment_data"] = enrichment_data
        else:
            context["has_enrichment"] = False
            context["enrichment_data"] = {}

        return context


class TWFDictionaryDictionaryEditView(FormView, TWFDictionaryView):
    """Edit a dictionary."""

    template_name = "twf/dictionaries/dictionary_edit.html"
    page_title = "Edit Dictionary"
    form_class = DictionaryForm
    success_url = reverse_lazy("twf:dictionaries")
    navigation_anchor = reverse_lazy("twf:dictionaries")

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["dictionary"] = (
            Dictionary.objects.get(pk=self.kwargs.get("pk"))
            if self.kwargs.get("pk")
            else None
        )
        return context

    def get_form_kwargs(self):
        """Get the form kwargs."""
        kwargs = super().get_form_kwargs()
        if self.kwargs.get("pk"):
            kwargs["instance"] = Dictionary.objects.get(pk=self.kwargs.get("pk"))
        return kwargs

    def form_valid(self, form):
        """Handle the form submission."""
        # Save the form
        form.instance.save(current_user=self.request.user)
        # Add a success message
        messages.success(
            self.request, "Dictionary settings have been updated successfully."
        )
        # Redirect to the success URL
        return super().form_valid(form)


class TWFDictionaryNormDataView(TWFDictionaryView):
    """Normalization Data Wizard."""

    template_name = "twf/dictionaries/normalization_wizard.html"
    page_title = "Normalization Data Wizard"
    navigation_anchor = reverse_lazy("twf:dictionaries_normalization")

    def post(self, request, *args, **kwargs):
        """Handle the POST request."""
        if "submit_geonames" in request.POST:
            logger.debug("Dictionary normalization - submit_geonames selected")
        elif "submit_gnd" in request.POST:
            logger.debug("Dictionary normalization - submit_gnd selected")
        elif "submit_wikidata" in request.POST:
            logger.debug("Dictionary normalization - submit_wikidata selected")
        elif "submit_openai" in request.POST:
            logger.debug("Dictionary normalization - submit_openai selected")

        return redirect("twf:dictionaries_normalization")

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        dictionaries = self.get_dictionaries()
        context["selected_dict"] = self.request.GET.get(
            "selected_dict", dictionaries[0].type
        )
        context["next_unenriched_entry"] = self.get_next_unenriched_entry(
            context["selected_dict"]
        )

        label = (
            context["next_unenriched_entry"].label
            if context["next_unenriched_entry"]
            else None
        )
        context["form_manual"] = EnrichEntryManualForm(
            instance=context["next_unenriched_entry"]
        )
        context["form_geonames"] = EnrichEntryForm(
            search_term=label, form_name="geonames"
        )
        context["form_gnd"] = EnrichEntryForm(search_term=label, form_name="gnd")
        context["form_wikidata"] = EnrichEntryForm(
            search_term=label, form_name="wikidata"
        )
        # context['form_openai'] = GeonamesBatchForm()

        return context

    def get_next_unenriched_entry(self, selected_dict):
        """Get the next unenriched entry."""
        dictionary = self.get_project().selected_dictionaries.get(type=selected_dict)
        entry = dictionary.entries.filter(metadata={}).order_by("modified_at").first()
        return entry


class TWFDictionaryMergeEntriesView(TWFDictionaryView):
    """Normalization Data Wizard."""

    template_name = "twf/dictionaries/merge_entries.html"
    page_title = "Merge Dictionary Entries"

    def post(self, request, *args, **kwargs):
        """Handle the POST request to merge entries."""
        remaining_entry_id = request.POST.get("remaining_entry")
        merge_entry_id = request.POST.get("merge_entry")

        if not remaining_entry_id or not merge_entry_id:
            messages.error(request, "Both entries must be selected.")
            return redirect(self.request.path)

        if remaining_entry_id == merge_entry_id:
            messages.error(request, "You cannot merge an entry into itself.")
            return redirect(self.request.path)

        try:
            remaining_entry = DictionaryEntry.objects.get(pk=remaining_entry_id)
            merge_entry = DictionaryEntry.objects.get(pk=merge_entry_id)
        except DictionaryEntry.DoesNotExist:
            messages.error(request, "One of the selected entries does not exist.")
            return redirect(self.request.path)

        # Step 1: Transfer PageTags
        PageTag.objects.filter(dictionary_entry=merge_entry).update(
            dictionary_entry=remaining_entry
        )

        # Step 2: Transfer Variations
        merge_variations = merge_entry.variations.all()
        for variation in merge_variations:
            # Reassign the variation to the remaining entry
            variation.entry = remaining_entry
            variation.save()

        # Step 3: Merge notes and authorization data
        remaining_entry.notes += f"\nMerged Notes:\n{merge_entry.notes}"
        for key, value in merge_entry.metadata.items():
            if key not in remaining_entry.metadata:
                remaining_entry.metadata[key] = value

        remaining_entry.save()

        # Step 4: Delete the merged entry
        merge_entry.delete()

        messages.success(
            request,
            f"Successfully merged entry '{merge_entry.label}' into '{remaining_entry.label}'.",
        )
        return redirect(self.request.path)

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        project = self.get_project()

        # Get all dictionaries in the project
        dictionaries = project.selected_dictionaries.all()

        # Fetch all entries from these dictionaries
        entries = (
            DictionaryEntry.objects.filter(dictionary__in=dictionaries)
            .select_related("dictionary")
            .order_by("dictionary__label", "label")
        )

        # Add formatted entries for display
        formatted_entries = [
            {"id": entry.id, "label": f"{entry.dictionary.label} - {entry.label}"}
            for entry in entries
        ]

        context["entries"] = formatted_entries
        return context


class TWFDictionaryDictionaryEntryEditView(FormView, TWFDictionaryView):
    """Edit a dictionary entry."""

    template_name = "twf/dictionaries/dictionary_entry_edit.html"
    page_title = "Edit Dictionary Entry"
    form_class = DictionaryEntryForm
    success_url = reverse_lazy("twf:dictionaries")
    navigation_anchor = reverse_lazy("twf:dictionaries")

    def get_form_kwargs(self):
        """Get the form kwargs."""
        kwargs = super().get_form_kwargs()
        if self.kwargs.get("pk"):
            kwargs["instance"] = self.get_entry()
        return kwargs

    def get_entry(self):
        """Get the dictionary entry."""
        try:
            return DictionaryEntry.objects.get(pk=self.kwargs.get("pk"))
        except DictionaryEntry.DoesNotExist:
            return None

    def get_breadcrumbs(self):
        """Get the breadcrumbs for dictionary entry edit view."""
        # Start with home and dictionaries section
        breadcrumbs = [
            {"url": reverse("twf:home"), "value": '<i class="fas fa-home"></i>'},
            {"url": reverse("twf:dictionaries_overview"), "value": "Dictionaries"},
            {"url": reverse("twf:dictionaries"), "value": "Dictionary List"},
        ]

        # Get the entry and its dictionary
        entry = self.get_entry()
        if entry:
            # Add the dictionary to the breadcrumbs
            breadcrumbs.append(
                {
                    "url": reverse("twf:dictionaries_view", args=[entry.dictionary.pk]),
                    "value": entry.dictionary.label,
                }
            )

            # Add the entry view as another level
            breadcrumbs.append(
                {
                    "url": reverse("twf:dictionaries_entry_view", args=[entry.pk]),
                    "value": entry.label,
                }
            )

            # Add the edit page
            breadcrumbs.append({"url": self.request.path, "value": "Edit"})

        return breadcrumbs

    def get_context_data(self, **kwargs):
        """Get the context data."""
        context = super().get_context_data(**kwargs)
        context["entry"] = self.get_entry()
        return context

    def form_valid(self, form):
        """Handle the form submission."""
        # Check if the delete button was pressed
        if "delete_entry" in self.request.POST:
            # Delete the entry
            entry = form.instance
            entry.delete()

            # Add a success message
            messages.success(
                self.request, "Dictionary Entry has been deleted successfully."
            )

            # Redirect to the success URL
            return redirect(self.success_url)

        # If the save button was pressed, save the form
        if "save_entry" in self.request.POST:
            form.instance.save(current_user=self.request.user)

            # Add a success message
            messages.success(
                self.request,
                "Dictionary Entry settings have been updated successfully.",
            )

            # Redirect to the dictionary view page instead of the dictionaries list
            if form.instance.pk:
                return redirect("twf:dictionaries_entry_view", pk=form.instance.pk)

            # Fallback to the success URL if something went wrong
            return super().form_valid(form)

        # If neither button matches, fallback to the default behavior
        return super().form_invalid(form)

class TWFDictionaryEnrichmentView(FormView, TWFDictionaryView):
    """Generic view for dictionary entry enrichment workflows."""

    template_name = "twf/dictionaries/enrichment_workflow.html"
    page_title = "Dictionary Enrichment"

    def get_enrichment_type(self):
        """Get enrichment type from workflow metadata."""
        workflow = self.get_active_workflow()
        if workflow and workflow.metadata:
            return workflow.metadata.get("enrichment_type")
        return None

    def get_form_class(self):
        """Return appropriate form class based on enrichment type."""
        workflow = self.get_active_workflow()
        if workflow and workflow.get_next_item():
            enrichment_type = self.get_enrichment_type()
            if enrichment_type:
                return get_enrichment_form_class(enrichment_type)
        return None

    def get_form(self, form_class=None):
        """Return form instance or None if no active workflow."""
        if form_class is None:
            form_class = self.get_form_class()
        if form_class is None:
            return None
        return super().get_form(form_class)

    def get_form_kwargs(self):
        """Add project and item to form kwargs."""
        kwargs = super().get_form_kwargs()
        workflow = self.get_active_workflow()
        if workflow:
            next_entry = workflow.get_next_item()
            if next_entry:
                kwargs["project"] = self.get_project()
                kwargs["item"] = next_entry
        return kwargs

    def get_active_workflow(self):
        """Get active dictionary enrichment workflow for current user."""
        return Workflow.objects.filter(
            project=self.get_project(),
            user=self.request.user,
            workflow_type="review_dictionary_enrichment",
            status="started",
        ).first()

    def post(self, request, *args, **kwargs):
        """Handle the post request."""
        # Handle workflow start
        if "start_workflow" in request.POST:
            dictionary_id = request.POST.get("dictionary_id")
            enrichment_type = request.POST.get("enrichment_type")
            batch_size = int(request.POST.get("batch_size", 20))
            
            if dictionary_id and enrichment_type:
                workflow = create_dictionary_enrichment_workflow(
                    self.get_project(), request.user, 
                    int(dictionary_id), enrichment_type, batch_size
                )
                if workflow:
                    messages.success(
                        request, f"Workflow started with {workflow.item_count} entries."
                    )
                else:
                    messages.error(
                        request, "No unenriched entries available for this dictionary and enrichment type."
                    )
            else:
                messages.error(request, "Invalid form data.")
            return redirect("twf:dictionaries_enrichment")

        # Handle enrichment form submission (when workflow is active)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        """Handle the form submission."""
        logger.debug("Dictionary enrichment form is valid")
        workflow = self.get_active_workflow()
        if not workflow:
            messages.error(self.request, "No active workflow found.")
            return redirect("twf:dictionaries_enrichment")

        # Save enrichment using form's save method
        form.save(user=self.request.user)
        messages.success(self.request, "Dictionary entry enriched successfully.")

        # Check workflow completion
        if not workflow.get_next_item():
            workflow.finish()
            messages.success(self.request, "Workflow completed!")

        return redirect("twf:dictionaries_enrichment")

    def get(self, request, *args, **kwargs):
        """Override the get method to handle workflow state."""
        workflow = self.get_active_workflow()

        # No active workflow - show workflow start options
        if not workflow:
            context = self.get_context_data()
            context["has_active_workflow"] = False
            return self.render_to_response(context)

        # Active workflow exists
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Get the context data."""
        project = self.get_project()
        workflow = self.get_active_workflow()

        # No active workflow - show start form
        if not workflow:
            context = super(FormView, self).get_context_data(**kwargs)
            # Get available dictionaries and enrichment types
            dictionaries = Dictionary.objects.filter(selected_projects=project)
            enrichment_types = [
                ("verse", "Bible Verse"),
                ("date", "Date"),
                ("authority_id", "Authority ID"),
            ]
            context["dictionaries"] = dictionaries
            context["enrichment_types"] = enrichment_types
            context["has_active_workflow"] = False
            return context

        # Active workflow exists
        context = super().get_context_data(**kwargs)
        context["has_active_workflow"] = True
        context["workflow"] = workflow
        context["workflow_progress"] = workflow.get_progress()

        next_entry = workflow.get_next_item()
        context["has_next_entry"] = next_entry is not None
        context["entry"] = next_entry
        context["workflow_title"] = (
            workflow.metadata.get("dictionary_title", "Dictionary") + " Enrichment"
        )
        context["enrichment_type"] = workflow.metadata.get("enrichment_type", "")

        return context
