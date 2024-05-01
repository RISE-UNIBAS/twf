import time
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.http import JsonResponse, StreamingHttpResponse

from main.metadata_manager import MetadataManager
from main.models import Project, Document


async def start_metadata_extraction(request, project_id):
    cache.set(f'{project_id}_extract-metadata-progress', 0)
    create_doc_metadata_async = sync_to_async(create_doc_metadata, thread_sensitive=True)
    await create_doc_metadata_async(project_id, request.user)
    return JsonResponse({'status': 'success'}, status=200)


def create_doc_metadata(project_id, extracting_user):
    auth_json = 'transkribusWorkflow/transkribusworkflow-a213551836b3.json'

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
            set_progress(processed_docs, total_documents, project_id)

        cache.set(f'{project.id}_extract-metadata-progress', 100)

    except Project.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Project not found.'}, status=404)


def stream_metadata_extraction_progress(request, project_id):
    cache.set(f'{project_id}_extract-metadata-progress', 0)

    def event_stream():
        while True:
            progress = cache.get(f'{project_id}_extract-metadata-progress', 0)
            yield f'data: {progress}\n\n'
            if progress >= 100:
                break
            time.sleep(1)  # Sleep for one second before checking again

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def set_progress(processed_steps, total_steps, project_id):
    """This function calculates the progress of a process and saves it to the cache."""
    progress = (processed_steps / total_steps) * 100
    progress = progress - 30
    if progress < 0:
        progress = 0
    cache.set(f'{project_id}_extract-metadata-progress', progress)
