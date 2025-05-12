"""Views for the project documents."""
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from twf.models import Document
from twf.utils.metadata_utils import delete_nested_key, set_nested_value
from twf.views.views_base import get_referrer_or_default


@login_required
def delete_document(request, pk, doc_pk):
    """Deletes a document."""
    document = get_object_or_404(Document, pk=doc_pk)
    for page in document.pages.all():
        page.xml_file.delete()
        page.delete()
    document.delete()
    messages.success(request, f'Document {doc_pk} has been deleted.')

    return get_referrer_or_default(request, default='twf:document')


def update_document_metadata(request, pk, base_key):
    if request.method == "POST":
        data = json.loads(request.body)
        key = data.get("key")
        value = data.get("value")

        try:
            doc = Document.objects.get(pk=pk)
            base = doc.metadata.get(base_key, {})
            set_nested_value(base, key, value)
            doc.metadata[base_key] = base
            doc.save(current_user=request.user)
        except Document.DoesNotExist:
            return JsonResponse({"error": "Document does not exist."}, status=404)

        return JsonResponse({"new_value": value})


@csrf_exempt
def delete_document_metadata(request, pk, base_key):
    if request.method == "POST":
        data = json.loads(request.body)
        key = data.get("key")

        try:
            doc = Document.objects.get(pk=pk)
            base = doc.metadata.get(base_key, {})
            delete_nested_key(base, key)
            doc.metadata[base_key] = base
            doc.save(current_user=request.user)
        except Document.DoesNotExist:
            return JsonResponse({"error": "Document does not exist."}, status=404)
        except KeyError:
            return JsonResponse({"error": "Key does not exist."}, status=404)

        return JsonResponse({"success": True})
