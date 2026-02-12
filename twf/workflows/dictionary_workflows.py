"""
Dictionary Workflow Management
===============================

This module provides functions for creating and managing dictionary-related workflows.
"""

from django.db.models import Q
from twf.models import Workflow, DictionaryEntry, Dictionary
from twf.tasks.instant_tasks import start_related_task


def create_dictionary_enrichment_workflow(project, user, dictionary_id, enrichment_type, item_count=None):
    """
    Create workflow for dictionary entry enrichment.

    Parameters
    ----------
    project : Project
        The project to create the workflow for
    user : User
        The user creating the workflow
    dictionary_id : int
        The dictionary ID to enrich entries from
    enrichment_type : str
        The enrichment type (e.g., 'verse', 'date', 'authority_id')
    item_count : int, optional
        Number of entries to enrich. If None, uses configured batch size.

    Returns
    -------
    bool or Workflow
        False if no entries available, otherwise the created Workflow instance
    """
    # Get the dictionary
    try:
        dictionary = Dictionary.objects.get(id=dictionary_id, selected_projects=project)
    except Dictionary.DoesNotExist:
        return False

    # Use configured batch size if not provided
    if item_count is None:
        workflow_def = project.get_workflow_definition("review_dictionary_enrichment")
        item_count = workflow_def.get("batch_size", 20)

    # Find unenriched entries in this dictionary
    # An entry is unenriched if it has no enrichment data for this specific type
    available_entries = []
    for entry in DictionaryEntry.objects.filter(
        dictionary=dictionary,
        is_reserved=False,
    )[:item_count * 2]:  # Get more to filter
        # Check if entry has this specific enrichment type
        if not entry.has_enrichment(enrichment_type):
            available_entries.append(entry.id)
            if len(available_entries) >= item_count:
                break

    if not available_entries:
        return False

    # Mark as reserved
    DictionaryEntry.objects.filter(id__in=available_entries).update(is_reserved=True)

    # Create task
    workflow_title = f"Enrich {dictionary.label} Entries ({enrichment_type})"
    task = start_related_task(
        project,
        user,
        workflow_title,
        f"Enrich dictionary entries with {enrichment_type} data.",
        f"The user has started a workflow to enrich {len(available_entries)} entries from '{dictionary.label}'.",
    )

    # Create workflow with metadata
    workflow = Workflow.objects.create(
        project=project,
        user=user,
        workflow_type="review_dictionary_enrichment",
        item_count=len(available_entries),
        related_task=task,
        metadata={
            "dictionary_id": dictionary_id,
            "dictionary_title": dictionary.label,
            "enrichment_type": enrichment_type,
        },
    )

    # Assign entries using the assigned_dictionary_entries M2M field
    workflow.assigned_dictionary_entries.set(
        DictionaryEntry.objects.filter(id__in=available_entries)
    )

    return workflow


def get_available_dictionary_entry_count(project, dictionary_id, enrichment_type):
    """
    Get count of unenriched entries in a dictionary for a specific enrichment type.

    Parameters
    ----------
    project : Project
        The project
    dictionary_id : int
        The dictionary ID
    enrichment_type : str
        The enrichment type to check

    Returns
    -------
    int
        Count of unenriched entries
    """
    try:
        dictionary = Dictionary.objects.get(id=dictionary_id, selected_projects=project)
    except Dictionary.DoesNotExist:
        return 0

    count = 0
    for entry in DictionaryEntry.objects.filter(
        dictionary=dictionary,
        is_reserved=False,
    ):
        if not entry.has_enrichment(enrichment_type):
            count += 1

    return count
