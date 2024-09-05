""""""
from asgiref.sync import sync_to_async
from django.http import JsonResponse, StreamingHttpResponse

from twf.metadata_manager import MetadataManager
from twf.models import Project, Document
from twf.views.views_ajax_base import set_progress, calculate_and_set_progress, base_event_stream

PROGRESS_JOB_NAME = "extract-meta-progress"
DETAIL_JOB_NAME = "extract-meta-progress-detail"


async def start_metadata_extraction(request):
    """This function starts the metadata extraction process."""
    project_id = request.session.get('project_id')
    set_progress(0, project_id, PROGRESS_JOB_NAME)
    create_doc_metadata_async = sync_to_async(create_doc_metadata, thread_sensitive=True)
    await create_doc_metadata_async(project_id, request.user)
    return JsonResponse({'status': 'success'}, status=200)


def create_doc_metadata(project_id, extracting_user):
    """This function extracts metadata from a Google Sheet and saves it to the documents in a project."""
    auth_json = 'transkribusWorkflow/google_key.json'

    try:
        # Get the projects to save the documents to
        project = Project.objects.get(pk=project_id)
        total_documents = Document.objects.filter(project=project).order_by('document_id').count()

        table_data = MetadataManager.get_data_from_spreadsheet(auth_json,
                                                               project.metadata_google_sheet_id,
                                                               project.metadata_google_sheet_range)

        title_row = table_data[0]
        table_data = table_data[1:]
        processed_docs = 0
        for d in table_data:
            doc_id = d[title_row.index(project.metadata_google_doc_id_column)]
            try:
                doc = Document.objects.get(document_id=doc_id)
                doc.title = d[title_row.index(project.metadata_google_title_column)]
                for col in project.get_valid_cols():
                    if col in title_row:
                        value = d[title_row.index(col)]
                        if value != '':
                            doc.metadata[col] = value
                doc.save()
                print("Updated metadata for document", doc_id)
            except Document.DoesNotExist:
                print(f"Document {doc_id} not found")
            calculate_and_set_progress(processed_docs, total_documents, project_id, PROGRESS_JOB_NAME)

        set_progress(100, project_id, PROGRESS_JOB_NAME)

    except Project.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Project not found.'}, status=404)


def stream_metadata_extraction_progress(request):
    project_id = request.session.get('project_id')
    set_progress(0, project_id, PROGRESS_JOB_NAME)

    return StreamingHttpResponse(base_event_stream(project_id, PROGRESS_JOB_NAME),
                                 content_type='text/event-stream')
