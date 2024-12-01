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
from twf.forms.project_forms import CollectionForm, CollectionAddDocumentForm
from twf.models import CollectionItem, Collection
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
