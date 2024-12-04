from django.contrib import messages
from django.shortcuts import redirect

from twf.models import Workflow, Document
from twf.tasks.instant_tasks import start_related_task
from twf.views.views_base import TWFView


def create_document_workflow(project, user, item_count):
    """
    Create a new workflow for reviewing documents and pre-select the documents.
    """
    # Get available document IDs that are not reserved and not reviewed
    available_document_ids = list(
        Document.objects.filter(project=project, is_reserved=False, status='open')
        .values_list('id', flat=True)[:item_count]
    )

    if len(available_document_ids) == 0:
        return False

    if len(available_document_ids) < item_count:
        item_count = len(available_document_ids)

    # Mark the documents as reserved
    Document.objects.filter(id__in=available_document_ids).update(is_reserved=True)

    task = start_related_task(project, user,
                              "Review Documents",
                              "Review documents in the project.",
                              "The user has started a workflow to review documents.")

    # Create the workflow
    workflow = Workflow.objects.create(
        project=project,
        user=user,
        workflow_type='review_documents',
        item_count=item_count,
        related_task=task
    )

    # Assign documents to the workflow
    workflow.assigned_document_items.set(Document.objects.filter(id__in=available_document_ids))

    return True



def start_review_document_workflow(request):

    project = TWFView.s_get_project(request)
    user = request.user

    started_workflow = create_document_workflow(project, user, 5)
    if not started_workflow:
        messages.error(request, "No documents available for review.")
        return redirect('twf:documents_review')

    return redirect('twf:documents_review')