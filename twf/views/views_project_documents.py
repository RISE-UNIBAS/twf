"""Views for the project documents."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from twf.filters import DocumentFilter
from twf.models import Document
from twf.tables import DocumentTable
from twf.views.views_base import BaseProjectListView, BaseProjectView


class ProjectDocumentView(SingleTableMixin, FilterView, BaseProjectListView):
    """View for the project documents."""
    template_name = 'twf/documents.html'
    table_class = DocumentTable
    model = Document
    filterset_class = DocumentFilter
    paginate_by = 10

    def get_queryset(self):
        # TODO: Filter by project
        return Document.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context.keys())
        return context


class DocumentView(BaseProjectView, TemplateView):
    """View for a single document."""
    template_name = 'twf/document.html'

    def get_context_data(self, **kwargs):
        """Add the project and document to the context."""
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        document = project.documents.get(pk=self.kwargs.get('doc_pk'))
        context['document'] = document
        return context


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

    return redirect('twf:project', pk=pk)
