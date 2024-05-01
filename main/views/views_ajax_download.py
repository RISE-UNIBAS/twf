""" This module contains the view functions for the AJAX download of the Transkribus export file. """
import datetime
import os
import threading

import requests
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from main.models import Project

# Dictionary to hold progress for each user/session
download_progress = {}


@require_http_methods(["GET"])
@csrf_exempt
def ajax_transkribus_download_export(request, project_id):
    """ Handles the request to start the download of the Transkribus export file. """

    session_key = request.session.session_key or 'default_key'

    try:
        project = Project.objects.get(pk=project_id)
        url = project.job_download_url
    except Project.DoesNotExist:
        url = None

    def download_thread():
        """ Download the file in a separate thread."""
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')
        if total_length is not None:
            total_length_int = int(total_length)
            downloaded = 0
            fs = FileSystemStorage()
            if not fs.exists('tmp'):
                os.makedirs(fs.path('tmp'))

            tmp_file_path = fs.path('tmp/transkribus_export.zip')
            with open(tmp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)
                        downloaded += len(chunk)
                        download_progress[session_key] = (downloaded / total_length_int) * 100

            with open(tmp_file_path, 'rb') as f:
                project.downloaded_zip_file.save(f'{project.collection_id}_export.zip', File(f))

            project.downloaded_at = datetime.datetime.now()
            project.save(current_user=request.user)
    threading.Thread(target=download_thread).start()
    return JsonResponse({'status': 'Download started'})


def download_progress_view(request):
    """ Returns the download progress for the current user/session. """
    session_key = request.session.session_key or 'default_key'
    progress = download_progress.get(session_key, 0)
    return JsonResponse({'progress': progress})
