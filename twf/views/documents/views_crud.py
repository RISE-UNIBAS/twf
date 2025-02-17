"""Views for the project documents."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

from twf.models import Document

@login_required
def delete_document(request, pk, doc_pk):
    """Deletes a document."""
    document = get_object_or_404(Document, pk=doc_pk)
    for page in document.pages.all():
        page.xml_file.delete()
        page.delete()
    document.delete()
    messages.success(request, f'Document {doc_pk} has been deleted.')

    # Get the HTTP referer URL
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)

    return redirect('twf:document', pk=pk)
