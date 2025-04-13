"""Views for the project documents."""
import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from twf.forms.filters.filters import DocumentFilter
from twf.forms.documents.documents_forms import DocumentForm, DocumentSearchForm
from twf.models import Document, Workflow
from twf.tables.tables_document import DocumentTable
from twf.views.views_base import TWFView

# Create a logger for this module
logger = logging.getLogger(__name__)


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
                    {'url': reverse('twf:documents_search'), 'value': 'Search Documents'},
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
                    {'url': reverse('twf:documents_batch_mistral'),
                     'value': 'Mistral', 'permission': 'document_batch_workflow_mistral'},
                ]
            },
            {
                'name': 'Page Batch',
                'options': [
                    {'url': reverse('twf:documents_page_batch_openai'),
                     'value': 'ChatGPT', 'permission': 'document_page_batch_workflow_openai'},
                    {'url': reverse('twf:documents_page_batch_gemini'),
                     'value': 'Gemini', 'permission': 'document_page_batch_workflow_gemini'},
                    {'url': reverse('twf:documents_page_batch_claude'),
                     'value': 'Claude', 'permission': 'document_page_batch_workflow_claude'},
                    {'url': reverse('twf:documents_page_batch_mistral'),
                     'value': 'Mistral', 'permission': 'document_page_batch_workflow_mistral'},
                ]
            },
            {
                'name': 'Manual Workflows',
                'options': [
                    {'url': reverse('twf:documents_review'),
                     'value': 'Review Documents', 'permission': 'document_task_review'},
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
    page_title = 'Documents'
    show_context_help = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_project()
        documents = project.documents.all()
        
        # Document statistics
        total_documents = documents.count()
        total_pages = sum(doc.pages.count() for doc in documents)
        
        # Average pages per document
        avg_pages = documents.annotate(num_pages=Count('pages')).aggregate(Avg('num_pages'))
        
        # Status counts
        completed_documents = documents.filter(status='completed').count()
        in_progress_documents = documents.filter(status='in_progress').count()
        parked_documents = documents.filter(is_parked=True).count()
        
        # Ignored documents statistics
        ignored_pages = sum(doc.pages.filter(is_ignored=True).count() for doc in documents)
        ignored_percentage = (ignored_pages / total_pages * 100) if total_pages > 0 else 0
        ignored_documents_count = documents.filter(is_parked=True).count()
        ignored_documents_percentage = (ignored_documents_count / total_documents * 100) if total_documents > 0 else 0

        # Gather metadata keys from all documents
        metadata_keys = set()
        for document in documents:
            if isinstance(document.metadata, dict):
                metadata_keys.update(document.metadata.keys())
        
        # Tag statistics
        from twf.models import PageTag
        project_tags = PageTag.objects.filter(page__document__project=project)
        total_tags = project_tags.count()
        open_tags = project_tags.filter(is_parked=False).count()
        resolved_tags = project_tags.filter(is_parked=True).count()
        
        # Calculate tags per page
        tags_per_page = total_tags / total_pages if total_pages > 0 else 0
        
        # Get tag types distribution
        tag_types = project_tags.values('variation_type').annotate(count=Count('id')).order_by('-count')[:5]
        
        # Get a sample document for preview (most recently created)
        sample_document = documents.order_by('-created_at').first()
        
        # Get recent documents (5 most recently modified)
        recent_documents = documents.order_by('-modified_at')[:5]
        
        # Create document statistics dictionary
        doc_stats = {
            'total_documents': total_documents,
            'total_pages': total_pages,
            'average_pages_per_document': avg_pages,
            'completed_documents': completed_documents,
            'in_progress_documents': in_progress_documents,
            'parked_documents': parked_documents,
            'ignored_pages': ignored_pages,
            'ignored_percentage': ignored_percentage,
            'ignored_documents': ignored_documents_count,
            'ignored_documents_percentage': ignored_documents_percentage,
        }
        
        # Create tag statistics dictionary
        tag_stats = {
            'total_tags': total_tags,
            'open_tags': open_tags,
            'resolved_tags': resolved_tags,
            'tags_per_page': tags_per_page,
            'tag_types': tag_types,
        }

        context.update({
            'doc_stats': doc_stats,
            'tag_stats': tag_stats,
            'metadata_keys': sorted(metadata_keys),
            'sample_document': sample_document,
            'recent_documents': recent_documents,
        })

        return context


class TWFDocumentsBrowseView(SingleTableView, FilterView, TWFDocumentView):
    """View for displaying project documents."""
    template_name = 'twf/documents/documents.html'
    page_title = 'Browse Documents'
    table_class = DocumentTable
    filterset_class = DocumentFilter
    paginate_by = 10
    model = Document
    strict = False

    def get_queryset(self):
        """Get the queryset for the view."""
        # Get all documents for the current project
        queryset = Document.objects.filter(project_id=self.request.session.get('project_id'))
        return queryset
    
    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        # Set up initial queryset
        queryset = self.get_queryset()
        
        # Initialize the filter
        self.filterset = self.filterset_class(
            request.GET or None,
            queryset=queryset
        )
        
        # Set object_list either to all items or filtered items
        if request.GET and self.filterset.is_bound:
            self.object_list = self.filterset.qs
        else:
            self.object_list = queryset
            
        # Log filter results for debugging
        logger.debug(f"Initial document queryset count: {queryset.count()}")
        if hasattr(self, 'filterset') and self.filterset:
            logger.debug(f"Filtered document queryset count: {self.filterset.qs.count()}")
        
        # Get context and render response
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['filter'] = self.filterset
        
        # Add document statistics
        project = self.get_project()
        all_documents = project.documents.all()
        
        # Document statistics for the header
        stats = {
            'total': all_documents.count(),
            'active': all_documents.filter(is_parked=False).count(),
            'ignored': all_documents.filter(is_parked=True).count(),
            'reviewed': all_documents.filter(status='reviewed').count()
        }
        context['document_stats'] = stats
        
        return context


class TWFDocumentsSearchView(FormView, TWFDocumentView):
    """View for searching documents."""
    template_name = 'twf/documents/search_documents.html'
    page_title = 'Search Documents'
    form_class = DocumentSearchForm
    success_url = reverse_lazy('twf:documents_search')

    def form_valid(self, form):
        """Handle the form submission."""
        # Add a success message
        logger.debug("WOULD SEARCH FOR DOCUMENTS HERE") # TODO: Implement search
        # Redirect to the success URL
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        return context


class TWFDocumentDetailView(TWFDocumentView):
    """View for displaying a document."""
    template_name = 'twf/documents/document.html'
    page_title = 'Document Detail'
    navigation_anchor = reverse_lazy("twf:documents_browse")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["document"] = Document.objects.get(pk=self.kwargs.get('pk'))
        return context

    def get_breadcrumbs(self):
        """Get the breadcrumbs for the view."""
        breadcrumbs = super().get_breadcrumbs()
        breadcrumbs.insert(-1, {'url': reverse('twf:documents_browse'), 'value': 'Browse Documents'})
        return breadcrumbs


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
