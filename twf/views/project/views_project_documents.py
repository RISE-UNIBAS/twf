"""Views for the project documents."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from twf.forms.project_forms import DocumentForm
from twf.models import Document
from twf.views.project.views_project import TWFProjectView, TWFProjectDocumentsView


class TWFProjectDocumentView(TWFProjectView):
    template_name = 'twf/project/document.html'
    page_title = 'Document'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.request.session.get('project_id')
        if project_id:
            context['document'] = Document.objects.get(pk=self.kwargs.get('pk'))
        return context


class TWFProjectDocumentCreateView(FormView, TWFProjectView):
    template_name = 'twf/project/create_document.html'
    page_title = 'Create Document'
    form_class = DocumentForm
    success_url = reverse_lazy('twf:project_documents')
    object = None

    def form_valid(self, form):
        # Save the form
        self.object = form.save(commit=False)
        self.object.project_id = self.request.session.get('project_id')
        self.object.save(current_user=self.request.user)

        # Add a success message
        messages.success(self.request, 'Document has been created successfully.')
        # Redirect to the success URL
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.request.session.get('project_id')
        context['context_sub_nav'] = TWFProjectDocumentsView.get_sub_pages()
        return context


class TWFProjectDocumentNameView(TWFProjectView):
    template_name = 'twf/project/name_documents.html'
    page_title = 'Name Documents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.request.session.get('project_id')
        context['context_sub_nav'] = TWFProjectDocumentsView.get_sub_pages()
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
