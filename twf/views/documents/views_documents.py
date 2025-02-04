"""Views for the project documents."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from twf.filters import DocumentFilter
from twf.forms.documents.document_forms import DocumentForm
from twf.models import Document, Workflow
from twf.tables.tables_document import DocumentTable
from twf.views.views_base import TWFView


class TWFDocumentView(LoginRequiredMixin, TWFView):
    """Base view for all project views."""
    template_name = None

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
                    {'url': reverse('twf:documents_batch_openai'),
                     'value': 'ChatGPT', 'permission': 'document_batch_workflow_openai'},
                    {'url': reverse('twf:documents_batch_gemini'),
                     'value': 'Gemini', 'permission': 'document_batch_workflow_gemini'},
                    {'url': reverse('twf:documents_batch_claude'),
                     'value': 'Claude', 'permission': 'document_batch_workflow_claude'},
                ]
            },
            {
                'name': 'Document Workflows',
                'options': [
                    {'url': reverse('twf:documents_review'),
                     'value': 'Review Documents', 'permission': 'document_task_review'},
                    {'url': reverse('twf:documents_create'),
                     'value': 'Manual Document Creation', 'permission': 'document_create'},
                ]
            },

        ]
        return sub_nav

    def get_navigation_index(self):
        """Get the navigation index."""
        return 2

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        return context


class TWFDocumentsOverviewView(TWFDocumentView):
    """View for the project documents overview."""
    template_name = 'twf/documents/overview.html'
    page_title = 'Project Documents Overview'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_project()
        documents = project.documents.all()

        # Total number of documents
        total_documents = documents.count()

        # Average number of pages per document
        avg_pages_per_document = documents.annotate(num_pages=Count('pages')).aggregate(Avg('num_pages'))[
                                     'num_pages__avg'] or 0

        # Number and percentage of ignored documents
        ignored_documents_count = documents.filter(is_parked=True).count()
        ignored_documents_percentage = (ignored_documents_count / total_documents * 100) if total_documents > 0 else 0

        # Gather metadata keys if metadata is available
        metadata_keys = set()
        for document in documents:
            if isinstance(document.metadata, dict):
                metadata_keys.update(document.metadata.keys())

        context.update({
            'total_documents': total_documents,
            'avg_pages_per_document': avg_pages_per_document,
            'ignored_documents_count': ignored_documents_count,
            'ignored_documents_percentage': ignored_documents_percentage,
            'metadata_keys': sorted(metadata_keys),
        })

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


class TWFDocumentReviewView(TWFDocumentView):
    """View for naming documents."""
    template_name = 'twf/documents/review_documents.html'
    page_title = 'Review Documents'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the current workflow
        workflow = Workflow.objects.filter(project=self.get_project(), workflow_type="review_documents",
                                           user=self.request.user, status='started').order_by('created_at').first()

        if not workflow:
            context['has_active_workflow'] = False
            return context

        context['has_active_workflow'] = True

        # Fetch the next document
        next_document = workflow.get_next_item()
        context['workflow'] = workflow
        context['document'] = next_document

        return context

    def post(self, request, *args, **kwargs):
        workflow = Workflow.objects.filter(project=self.get_project(), workflow_type="review_documents",
                                           user=self.request.user, status='started').order_by('created_at').first()

        if not workflow:
            messages.error(request, "No active workflow found.")
            return redirect('twf:documents_review')  # Replace with the actual name of the review URL

        document_id = request.POST.get('document_id')
        action = request.POST.get('action')

        if document_id and action:
            document = Document.objects.filter(id=document_id).first()

            if document:
                # Mark the document based on user action
                if action == 'set_reviewed':
                    document.status = 'reviewed'
                elif action == 'set_parked':
                    document.is_parked = True
                elif action == 'set_irrelevant':
                    document.status = 'irrelevant'
                elif action == 'set_needs_work':
                    document.status = 'needs_tk_work'

                document.save()

                # Log the action in the workflow if needed
                if workflow.has_more_items():
                    workflow.advance()
                else:
                    workflow.finish()

        return redirect('twf:documents_review')
