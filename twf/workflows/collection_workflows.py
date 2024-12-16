from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

from twf.models import Workflow, Document, CollectionItem, Collection
from twf.tasks.instant_tasks import start_related_task
from twf.views.views_base import TWFView


def create_collection_workflow(project, user, collection, item_count):
    """
    Create a new workflow for reviewing documents and pre-select the documents.
    """
    # Get available document IDs that are not reserved and not reviewed
    available_collection_item_ids = list(
        CollectionItem.objects.filter(collection=collection,
                                      is_reserved=False, status='open')
        .values_list('id', flat=True)[:item_count]
    )

    if len(available_collection_item_ids) == 0:
        return False

    if len(available_collection_item_ids) < item_count:
        item_count = len(available_collection_item_ids)

    # Mark the documents as reserved
    CollectionItem.objects.filter(id__in=available_collection_item_ids).update(is_reserved=True)

    task = start_related_task(project, user,
                              "Review Collection",
                              "Review collection items a collection in the project.",
                              "The user has started a workflow to review documents.")

    # Create the workflow
    workflow = Workflow.objects.create(
        project=project,
        collection=collection,
        user=user,
        workflow_type='review_collection',
        item_count=item_count,
        related_task=task
    )

    # Assign documents to the workflow
    workflow.assigned_collection_items.set(CollectionItem.objects.filter(id__in=available_collection_item_ids))

    return True



def start_review_collection_workflow(request, collection_id):

    project = TWFView.s_get_project(request)
    user = request.user
    collection = Collection.objects.get(pk=collection_id)

    started_workflow = create_collection_workflow(project, user, collection, 5)
    if not started_workflow:
        messages.error(request, "No items available for review.")
        return redirect('twf:collections_review')

    return redirect('twf:collections_review')