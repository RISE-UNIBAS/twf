"""Views for the project documents."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from twf.filters import DocumentFilter
from twf.forms.documents.document_forms import DocumentForm
from twf.models import Document
from twf.tables.tables import DocumentTable
from twf.views.views_base import TWFView


class TWFDocumentView(LoginRequiredMixin, TWFView):
    """Base view for all project views."""
    template_name = 'twf/project/overview.html'

    def get_sub_navigation(self):
        """Get the sub navigation."""
        sub_nav = [
            {
                'name': 'Your Documents',
                'options': [
                    {'url': reverse('twf:documents_overview'), 'value': 'Overview'},
                    {'url': reverse('twf:documents_browse'), 'value': 'Browse Documents'},
                ]
            },
            {
                'name': 'Document Batch',
                'options': [
                    {'url': reverse('twf:documents_batch_openai'), 'value': 'ChatGPT'},
                    {'url': reverse('twf:documents_batch_gemini'), 'value': 'Gemini'},
                    {'url': reverse('twf:documents_batch_claude'), 'value': 'Claude'},
                ]
            },
            {
                'name': 'Create Documents',
                'options': [
                    {'url': reverse('twf:documents_create'), 'value': 'Manual Document Creation'},
                ]
            },

        ]
        return sub_nav

    def get_navigation_index(self):
        return 2

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TWFDocumentsOverviewView(TWFDocumentView):
    """View for the project documents overview."""
    template_name = 'twf/documents/overview.html'
    page_title = 'Project Documents Overview'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TWFDocumentsBrowseView(SingleTableView, FilterView, TWFDocumentView):
    """View for displaying project documents."""
    template_name = 'twf/documents/documents.html'
    page_title = 'Project Documents'
    table_class = DocumentTable
    filterset_class = DocumentFilter
    paginate_by = 10
    model = Document

    def get_queryset(self):
        """Get the queryset for the view."""
        queryset = Document.objects.filter(project_id=self.request.session.get('project_id'))
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get(self, request, *args, **kwargs):
        """Get the view."""
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['filter'] = self.get_filterset(self.filterset_class)
        return context


class TWFDocumentCreateView(FormView, TWFDocumentView):
    """View for creating a document."""
    template_name = 'twf/documents/create_document.html'
    page_title = 'Create Document'
    form_class = DocumentForm
    success_url = reverse_lazy('twf:documents_overview')
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
        return context


class TWFDocumentDetailView(TWFDocumentView):
    """View for displaying a document."""
    template_name = 'twf/documents/document.html'
    page_title = 'Document Detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["document"] = Document.objects.get(pk=self.kwargs.get('pk'))
        return context


class TWFDocumentNameView(TWFDocumentView):
    """View for naming documents."""
    template_name = 'twf/documents/name_documents.html'
    page_title = 'Name Documents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
