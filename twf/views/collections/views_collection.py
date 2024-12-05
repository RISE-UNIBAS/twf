""" This module contains the views for the Collection model. """
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from twf.filters import CollectionItemFilter
from twf.forms.dictionaries.collection_forms import CollectionOpenaiBatchForm
from twf.forms.project_forms import CollectionForm, CollectionAddDocumentForm
from twf.models import CollectionItem, Collection, Workflow
from twf.tables.tables_collection import CollectionItemTable
from twf.views.views_base import TWFView


class TWFCollectionsView(LoginRequiredMixin, TWFView):
    """ View for the project collections page. """

    template_name = 'twf/collections/collections.html'
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


class TWFProjectCollectionsCreateView(FormView, TWFCollectionsView):
    """ View for creating a new collection. """

    template_name = 'twf/collections/collections_create.html'
    page_title = 'Create New Collection'
    form_class = CollectionForm
    success_url = reverse_lazy('twf:collections')

    def form_valid(self, form):
        """Save the form and redirect to the success URL."""
        # Save the form
        self.object = form.save(commit=False)
        self.object.project_id = self.request.session.get('project_id')
        self.object.save(current_user=self.request.user)

        all_documents = self.get_project().documents.all()
        for doc in all_documents:
            item = CollectionItem(document=doc, collection=self.object, document_configuration={'annotations': []})
            item.title = f'Song in {doc.document_id}'
            for page in doc.get_active_pages():
                annotations = page.get_annotations()
                anno_types = []
                for annotation in annotations:
                    if "type" not in annotation:
                        print(f"Skipping annotation without type: {annotation}")
                        continue
                    anno_types.append(annotation['type'])
                    if annotation['type'] in ['lyrics', 'music', 'heading']:
                        item.document_configuration['annotations'].append(annotation)
            item.save(current_user=self.request.user)

        # Add a success message
        messages.success(self.request, 'Collection has been created successfully.')
        # Redirect to the success URL
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Get the context data for the view."""
        context = super().get_context_data(**kwargs)
        return context


class TWFProjectCollectionsDetailView(SingleTableView, FilterView, TWFCollectionsView):
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
        context['page_title'] = self.page_title
        context['filter'] = self.get_filterset(self.filterset_class)
        return context


class TWFProjectCollectionsAddDocumentView(FormView, TWFCollectionsView):
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


class TWFProjectCollectionsReviewView(TWFCollectionsView):
    """ View for reviewing collection items. """
    template_name = 'twf/collections/collection_review.html'
    page_title = 'Review Collection Item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection = Collection.objects.get(pk=self.kwargs.get('pk'))

        # Fetch the first item not flagged as correct
        item = collection.items.filter(status__in=['open', '', None]).first()
        context['item'] = item
        context['collection'] = collection

        return context


class SplitCollectionItemView(View):
    """ View for splitting a collection item into two parts. """

    def post(self, request, pk, part_id):
        """ Split the collection item into two parts. """
        item = CollectionItem.objects.get(pk=pk)
        parts = item.document_configuration["annotations"]

        # Split parts into two sets
        first_half = parts[:part_id]
        second_half = parts[part_id:]

        # Duplicate the base configuration for both new items
        new_item1 = CollectionItem(title=item.title + "(Part 1 of a split)",
                                   collection_id=item.collection_id,
                                   document_configuration={"annotations": first_half},
                                   document=item.document)
        new_item1.save(current_user=request.user)
        new_item2 = CollectionItem(title=item.title + "(Part 2 of a split)",
                                   collection_id=item.collection_id,
                                   document_configuration={"annotations": second_half},
                                   document=item.document)
        new_item2.save(current_user=request.user)

        # Mark the original item as split or deleted
        item.delete()
        messages.success(request, "The item has been split into two parts.")

        return redirect('twf:project_collection_review', pk=item.collection.pk)


class RemovePartView(View):
    """ View for removing a part from a collection item. """

    def post(self, request, item_id, part_id):
        """ Remove the part from the collection item. """
        item = CollectionItem.objects.get(pk=item_id)
        parts = item.document_configuration['annotations']

        # Remove the part with the given ID
        del(parts[part_id-1])
        item.document_configuration['annotations'] = parts
        item.save(current_user=request.user)
        messages.success(request, "The part has been removed from the item.")

        return redirect('twf:project_collection_review', pk=item.collection.pk)


class UpdateCollectionItemView(View):
    """ View for updating a collection item. """

    def post(self, request, pk):
        """ Update the collection item with the new information. """
        # Get the item to be updated
        item = CollectionItem.objects.get(pk=pk)

        # Update the title from the form input
        new_title = request.POST.get('item_title')
        item.title = new_title

        # Update the status from the form input
        new_status = request.POST.get('item_status')
        item.status = new_status

        notes = request.POST.get('notes')
        item.review_notes = notes

        # Save the updated item
        item.save(current_user=request.user)
        messages.success(request, 'The item has been updated successfully.')

        return redirect('twf:project_collection_review', pk=item.collection.pk)


class TWFCollectionsReviewView(TWFCollectionsView):
    """View for naming documents."""
    template_name = 'twf/collections/review_collections.html'
    page_title = 'Review Collections'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch the current workflow
        workflow = Workflow.objects.filter(project=self.get_project(), workflow_type="review_collection",
                                           user=self.request.user, status='started').order_by('created_at').first()

        context['collections'] = Collection.objects.filter(project=self.get_project())

        if not workflow:
            context['has_active_workflow'] = False
            return context

        context['has_active_workflow'] = True

        # Fetch the next document
        next_item = workflow.get_next_item()
        context['workflow'] = workflow
        context['collection_item'] = next_item

        return context

    def post(self, request, *args, **kwargs):
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

        return redirect('twf:collections_review')


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
        kwargs['data-progress-url-base'] = "/celery/status/"
        kwargs['data-progress-bar-id'] = "#taskProgressBar"
        kwargs['data-log-textarea-id'] = "#id_progress_details"

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
        kwargs['data-progress-url-base'] = "/celery/status/"
        kwargs['data-progress-bar-id'] = "#taskProgressBar"
        kwargs['data-log-textarea-id'] = "#id_progress_details"

        return kwargs