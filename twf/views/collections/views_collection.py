""" This module contains the views for the Collection model. """
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from twf.filters import CollectionItemFilter
from twf.forms.dictionaries.collection_forms import CollectionOpenaiBatchForm
from twf.forms.collection_forms import CollectionCreateForm, CollectionAddDocumentForm, CollectionUpdateForm, \
    CollectionItemReviewForm, CollectionItemUpdateForm
from twf.models import CollectionItem, Collection, Workflow
from twf.permissions import check_permission
from twf.tables.tables_collection import CollectionItemTable
from twf.views.collections.views_crud import fill_collection_item, clean_annotation
from twf.views.views_base import TWFView


class TWFCollectionsView(LoginRequiredMixin, TWFView):
    """ View for the project collections page. """

    template_name = None
    page_title = 'Project Collections'

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        context['collections'] = Collection.objects.filter(project_id=self.request.session.get('project_id'))
        return context

    def get_sub_navigation(self):
        """Get the sub-navigation for the view."""
        sub_nav = [
            {
                'name': 'Overview',
                'options': [
                    {"url": reverse('twf:collections'), "value": "Overview"},
                    {"url": reverse('twf:project_collections_create'), "value": "Create New Collection"},
                ]
            },
            {
                'name': 'Your collections',
                'options': []
            },
            {
                'name': 'Collection Workflows',
                'options': [
                    {"url": reverse('twf:collections_review'), "value": "Review Collections"},
                    {"url": reverse('twf:collections_openai_batch'), "value": "OpenAI Batch Workflow"},
                    {"url": reverse('twf:collections_openai_request'), "value": "OpenAI Single Workflow"},
                    {"url": "", "value": "Name Collection Items"},
                    {"url": "", "value": "Merge Collection Items"},
                ]
            }
        ]

        collections = Collection.objects.filter(project=self.get_project())
        for collection in collections:
            sub_nav[1]['options'].append({
                'url': reverse('twf:collections_view', kwargs={'pk': collection.pk}),
                'value': collection.title
            })

        return sub_nav

    def get_navigation_index(self):
        """Get the index of the navigation item."""
        return 6


class TWFCollectionOverviewView(TWFCollectionsView):
    """ View for the collection overview page. """

    template_name = 'twf/collections/collections_overview.html'
    page_title = 'Collection Overview'

    def post(self, request, *args, **kwargs):
        """Handle the post request."""
        print(request.POST)
        if "delete_collection" in request.POST:
            collection = Collection.objects.get(pk=request.POST.get('collection_id'))
            collection.delete()
            messages.success(request, 'Collection has been deleted successfully.')

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)

        open_workflows = Workflow.objects.filter(project=self.get_project(), workflow_type="review_collection",
                                                 status='started').count()
        total_items = CollectionItem.objects.filter(collection__project=self.get_project()).count()
        reviewed_items = CollectionItem.objects.filter(collection__project=self.get_project(),
                                                       status='reviewed').count()
        percentage_reviewed = reviewed_items / total_items * 100 if total_items > 0 else 0

        context['open_workflows'] = open_workflows
        context['percentage_reviewed'] = percentage_reviewed

        return context

class TWFCollectionsEditView(FormView, TWFCollectionsView):
    """ View for creating a new collection. """

    template_name = 'twf/collections/collections_edit.html'
    page_title = 'Edit Collection'
    form_class = CollectionUpdateForm
    success_url = reverse_lazy('twf:collections')

    def get_initial(self):
        """Initialize form with the object's data."""
        self.object = get_object_or_404(Collection, pk=self.kwargs['pk'])
        return {
            'title': self.object.title,
            'description': self.object.description,
        }

    def form_valid(self, form):
        """Handle valid form submission."""
        collection = get_object_or_404(Collection, pk=self.kwargs['pk'])
        collection.title = form.cleaned_data['title']
        collection.description = form.cleaned_data['description']
        collection.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add additional context data if needed."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context


class TWFCollectionItemView(TWFCollectionsView):
    """ View for viewing a collection item. """

    template_name = 'twf/collections/collection_item_view.html'
    page_title = 'View Collection Item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = CollectionItem.objects.get(pk=self.kwargs['pk'])
        return context

class TWFCollectionItemEditView(FormView, TWFCollectionsView):
    """ View for editing a collection item. """

    template_name = 'twf/collections/collection_item_edit.html'
    page_title = 'Edit Collection Item'
    form_class = CollectionItemUpdateForm

    def get_form_kwargs(self):
        """Pass instance to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = get_object_or_404(CollectionItem, pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        """Handle valid form submission."""
        form.instance.title = form.cleaned_data['title']
        form.instance.review_notes = form.cleaned_data['review_notes']
        form.instance.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the success URL with the pk of the form instance."""
        item = get_object_or_404(CollectionItem, pk=self.kwargs['pk'])
        return reverse('twf:collections_view', kwargs={'pk': item.collection.pk})

    def get_context_data(self, **kwargs):
        """Add additional context data if needed."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context


class TWFCollectionsCreateView(FormView, TWFCollectionsView):
    """ View for creating a new collection. """

    template_name = 'twf/collections/collections_create.html'
    page_title = 'Create New Collection'
    form_class = CollectionCreateForm
    success_url = reverse_lazy('twf:collections')

    def form_valid(self, form):
        """Save the form and redirect to the success URL."""
        # Save the form
        self.object = form.save(commit=False)
        self.object.project = self.get_project()
        self.object.save(current_user=self.request.user)

        # Create collection items according to the creation routine
        routine = form.cleaned_data['creation_routine']
        structure_tag_filter = form.cleaned_data['structure_tag_filter']
        structure_tag_filter_list = structure_tag_filter.split(',')
        skip_empty_types = form.cleaned_data['skip_empty_types']

        if routine == 'manual':
           messages.success(self.request, 'Collection has been created successfully. '
                                          'You now can items to the collection.')
        elif routine == 'an_item_per_document':
            all_documents = self.get_project().documents.all()
            for doc in all_documents:
                item = CollectionItem(document=doc, collection=self.object, document_configuration={'annotations': []})
                item.title = f'Item for {doc.document_id}'
                for page in doc.get_active_pages():
                    fill_collection_item(item, page, skip_empty_types, structure_tag_filter_list)
                item.save(current_user=self.request.user)
            messages.success(self.request, 'Collection has been created successfully. '
                                           'An item has been created for each document.')
        elif routine == 'an_item_per_page':
            all_documents = self.get_project().documents.all()
            for doc in all_documents:
                for page in doc.get_active_pages():
                    item = CollectionItem(document=doc, collection=self.object, document_configuration={'annotations': []})
                    item.title = f'Item in {doc.document_id} - Page {page.tk_page_number}'
                    fill_collection_item(item, page, skip_empty_types, structure_tag_filter_list)
                    item.save(current_user=self.request.user)
            messages.success(self.request, 'Collection has been created successfully. '
                                           'An item has been created for each page.')
        elif routine == 'structure_tag_based':
            all_documents = self.get_project().documents.all()
            structure_tags = []
            for doc in all_documents:
                for page in doc.get_active_pages():
                    annotations = page.get_annotations()
                    for annotation in annotations:
                        cleaned_annotation = clean_annotation(annotation)
                        if cleaned_annotation['type'] not in structure_tags:
                            structure_tags.append(cleaned_annotation['type'])

            for tag in structure_tags:
                item = CollectionItem(collection=self.object, document_configuration={'annotations': []})
                item.title = f'Item for structure tag: {tag}'
                for doc in all_documents:
                    for page in doc.get_active_pages():
                        annotations = page.get_annotations()
                        for annotation in annotations:
                            cleaned_annotation = clean_annotation(annotation)
                            if cleaned_annotation['type'] == tag:
                                item.document_configuration['annotations'].append(cleaned_annotation)

                item.save(current_user=self.request.user)
            messages.success(self.request, 'Collection has been created successfully. '
                                           'An item has been created for each structure tag.')


        # Redirect to the success URL
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        return context


class TWFCollectionsDetailView(SingleTableView, FilterView, TWFCollectionsView):
    """ View for the collection detail page. """

    template_name = "twf/collections/collection_view.html"
    page_title = 'View Collection'
    table_class = CollectionItemTable
    filterset_class = CollectionItemFilter
    paginate_by = 10
    model = CollectionItem

    def get_queryset(self):
        """Get the queryset for the view."""
        queryset = CollectionItem.objects.filter(collection_id=self.kwargs.get("pk"))
        self.filterset = self.filterset_class(self.request.GET, queryset=queryset)
        self.object_list = self.filterset.qs
        return self.object_list

    def get(self, request, *args, **kwargs):
        """Get the view."""
        self.object_list = self.get_queryset()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        context['collection'] = Collection.objects.get(pk=self.kwargs.get('pk'))
        context['page_title'] = self.page_title
        context['filter'] = self.get_filterset(self.filterset_class)
        return context


class TWFCollectionsAddDocumentView(FormView, TWFCollectionsView):
    """ View for adding a document to a collection. """

    template_name = 'twf/collections/collections_add_doc.html'
    page_title = 'Add Document To Collection'
    form_class = CollectionAddDocumentForm
    success_url = reverse_lazy('twf:collections')

    def form_valid(self, form):
        """Save the form and redirect to the success URL."""
        # Save the form
        doc = form.cleaned_data['document']
        collection = Collection.objects.get(pk=self.kwargs.get('pk'))
        collection_item = CollectionItem(document=doc, collection=collection)
        collection_item.save(current_user=self.request.user)

        # Add a success message
        messages.success(self.request, 'Document has been added to the collection successfully.')

        # Redirect to the success URL
        return super().form_valid(form)

    def get_form_kwargs(self):
        """Get the form keyword arguments."""
        kwargs = super().get_form_kwargs()
        # Add your custom argument here
        kwargs['collection'] = Collection.objects.get(pk=self.kwargs.get('pk'))
        return kwargs

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        return context


class TWFCollectionsReviewView(FormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/review_collections.html'
    page_title = 'Review Collections'
    form_class = CollectionItemReviewForm
    next_item = None
    workflow = None
    workflow_active = False

    def setup(self, request, *args, **kwargs):
        """Setup method to initialize workflow and next item."""
        super().setup(request, *args, **kwargs)

        self.workflow = Workflow.objects.filter(project=self.get_project(), workflow_type="review_collection",
                                                user=self.request.user, status='started').order_by('created_at').first()
        if self.workflow:
            self.workflow_active = True
            self.next_item = self.workflow.get_next_item()


    def get_form_kwargs(self):
        """Pass instance to the form."""
        kwargs = super().get_form_kwargs()
        if self.next_item:
            kwargs['instance'] = get_object_or_404(CollectionItem, pk=self.next_item.pk)
        return kwargs

    def form_valid(self, form):
        """Handle valid form submission."""
        action_r = self.request.POST.get('submit-r')
        action_f = self.request.POST.get('submit-f')
        action_d = self.request.POST.get('submit-d')
        action_u = self.request.POST.get('submit-u')

        if action_d:
            print("Deleting item", self.next_item)
            if check_permission(self.request.user, 'collection_item_delete', self.next_item.id):
                self.next_item.delete()
                messages.success(self.request, 'Collection item has been deleted successfully.')
            else:
                messages.error(self.request, 'You do not have permission to delete this collection item.')
        elif action_r or action_f:
            print("Updating item and continuing", self.next_item)
            self.next_item.title = form.cleaned_data['title']
            self.next_item.review_notes = form.cleaned_data['review_notes']

            if action_r:
                self.next_item.status = 'reviewed'
            if action_f:
                self.next_item.status = 'faulty'
            self.next_item.save()

            if self.workflow.has_more_items():
                self.workflow.advance()
            else:
                self.workflow.finish()
        elif action_u:
            print("Updating item", self.next_item)
            print(form.cleaned_data['title'])
            print(form.cleaned_data['review_notes'])
            self.next_item.title = form.cleaned_data['title']
            self.next_item.review_notes = form.cleaned_data['review_notes']
            self.next_item.save()
            messages.success(self.request, 'Collection item has been updated successfully.')

        return super().form_valid(form)

    def get_success_url(self):
        """Return the success URL with the pk of the form instance."""
        return reverse('twf:collections_review')

    def get_context_data(self, **kwargs):
        """Add additional context data if needed."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title

        context['collections'] = Collection.objects.filter(project=self.get_project())

        if not self.workflow_active:
            context['has_active_workflow'] = False
            return context

        context['has_active_workflow'] = True

        # Fetch the next document
        context['workflow'] = self.workflow
        context['collection_item'] = self.next_item

        return context

    """def post(self, request, *args, **kwargs):
        
        workflow = Workflow.objects.filter(project=self.get_project(), workflow_type="review_collection",
                                           user=self.request.user, status='started').order_by('created_at').first()

        if not workflow:
            messages.error(request, "No active workflow found.")
            return redirect('twf:collections_review')  #

        collection_item_id = request.POST.get('document_id')
        action = request.POST.get('action')

        if collection_item_id and action:
            collection_item = CollectionItem.objects.filter(id=collection_item_id).first()

            if collection_item:
                # Mark the document based on user action
                if action == 'set_reviewed':
                    collection_item.status = 'reviewed'
                elif action == 'set_parked':
                    collection_item.is_parked = True
                elif action == 'set_faulty':
                    collection_item.status = 'faulty'

                collection_item.save(current_user=request.user)

                # Log the action in the workflow if needed
                if workflow.has_more_items():
                    workflow.advance()
                else:
                    workflow.finish()

        return redirect('twf:collections_review')"""


class TWFCollectionsOpenaiBatchView(FormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/openai_batch.html'
    page_title = 'OpenAI Batch Workflow'
    form_class = CollectionOpenaiBatchForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_collection_batch_openai')
        kwargs['data-message'] = "Are you sure you want to start the openai task?"

        return kwargs



class TWFCollectionsOpenaiRequestView(FormView, TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/openai_request.html'
    page_title = 'OpenAI Request'
    form_class = CollectionOpenaiBatchForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['project'] = self.get_project()

        kwargs['data-start-url'] = reverse_lazy('twf:task_collection_request_openai')
        kwargs['data-message'] = "Are you sure you want to start the openai task?"

        return kwargs