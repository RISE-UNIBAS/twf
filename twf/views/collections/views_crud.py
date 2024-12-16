"""Views for CRUD operations on collections. These views do not render
HTML pages, but redirect to the appropriate URL after the operation is
completed."""
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from twf.models import Collection, CollectionItem, Workflow
from twf.permissions import check_permission

def delete_collection_item_annotation(request, pk, index):
    """Delete an annotation from a collection item."""
    is_allowed = check_permission(request.user,
                                  "collection_item_delete_annotation",
                                  pk)
    if not is_allowed:
        messages.error(request, "You do not have permission to delete annotations from this collection item.")
        return redirect('twf:collections')

    collection_item = CollectionItem.objects.get(id=pk)
    collection_item.delete_annotation(index)
    messages.success(request, "Annotation deleted.")

    if request.GET.get('redirect_to_view'):
        return redirect(request.GET.get('redirect_to_view'))

    return redirect('twf:collection_item_edit', pk=pk)


def delete_collection_item(request, pk):
    """Delete a collection item."""
    is_allowed = check_permission(request.user,
                                  "collection_item_delete",
                                  pk)
    if not is_allowed:
        messages.error(request, "You do not have permission to delete this collection item.")
        return redirect('twf:collections')

    collection_item = CollectionItem.objects.get(id=pk)
    collection_id = collection_item.collection.id
    collection_item.delete()
    messages.success(request, "Collection item deleted.")

    if request.GET.get('redirect_to_view'):
        return redirect(request.GET.get('redirect_to_view'))

    return redirect('twf:collections_view', pk=collection_id)


def copy_collection_item(request, pk):
    """Copy a collection item."""
    # Check user permission
    if not check_permission(request.user, "collection_item_copy", pk):
        messages.error(request, "You do not have permission to copy this collection item.")
        return redirect('twf:collections')

    # Get the collection item and perform the copy
    try:
        collection_item = CollectionItem.objects.get(id=pk)
        new_item = collection_item
        new_item.title = f"{collection_item.title} (copy)"
        new_item.pk = None
        new_item.save(current_user=request.user)

        if new_item is None:
            messages.error(request, "Could not copy collection item.")
        else:
            edit_url = reverse_lazy('twf:collection_item_edit', args=[new_item.id])
            messages.success(request, mark_safe(f'Collection item copied successfully! <a href="{edit_url}">Edit the new item</a>'))
    except CollectionItem.DoesNotExist:
        messages.error(request, "Collection item not found.")
    except Exception as e:
        messages.error(request, "An unexpected error occurred while copying the collection item.")

    if request.GET.get('redirect_to_view'):
        return redirect(request.GET.get('redirect_to_view'))

    return redirect('twf:collection_item_edit', pk=pk)


def split_collection_item(request, pk, index):
    """Split a collection item."""
    # Check user permission
    if not check_permission(request.user, "collection_item_split", pk):
        messages.error(request, "You do not have permission to split this collection item.")
        return redirect('twf:collections')

    # Get the collection item and perform the split
    try:
        collection_item = CollectionItem.objects.get(id=pk)
        new_item = collection_item.split(index, request.user)

        if new_item is None:
            messages.error(request, "Could not split collection item. Please check the index and try again.")
        else:
            edit_url = reverse_lazy('twf:collection_item_edit', args=[new_item.id])
            messages.success(request, mark_safe(f'Collection item split successfully! <a href="{edit_url}">Edit the new item</a>'))
    except CollectionItem.DoesNotExist:
        messages.error(request, "Collection item not found.")
    except Exception as e:
        messages.error(request, "An unexpected error occurred while splitting the collection item.")

    if request.GET.get('redirect_to_view'):
        return redirect(request.GET.get('redirect_to_view'))

    return redirect('twf:collection_item_edit', pk=pk)


def download_collection_item_txt(request, pk):
    """Download the text of a collection item as a .txt file."""

    item = CollectionItem.objects.get(id=pk)
    text = f"Title: {item.title}\n"
    for annotation in item.document_configuration['annotations']:
        text += f"\n{annotation['text']}\n"

    response = HttpResponse(text, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{item.title}.txt"'
    return response


def download_collection_item_json(request, pk):
    """Download the annotations of a collection item as a .json file."""

    item = CollectionItem.objects.get(id=pk)
    json = item.document_configuration
    json['title'] = item.title
    response = HttpResponse(json, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{item.title}.json"'
    return response


def set_col_item_status_open(request, pk):
    """Set the status of a collection item to open."""
    return set_col_item_status(request, pk, 'open')


def set_col_item_status_reviewed(request, pk):
    """Set the status of a collection item to reviewed."""
    return set_col_item_status(request, pk, 'reviewed')


def set_col_item_status_faulty(request, pk):
    """Set the status of a collection item to faulty."""
    return set_col_item_status(request, pk, 'faulty')


def set_col_item_status(request, collection_item_id, status):
    """Set the status of a collection item to open."""
    is_allowed = check_permission(request.user,
                                  "change_collection_item_status",
                                  collection_item_id)
    if not is_allowed:
        messages.error(request, "You do not have permission to change the status of this collection item.")
        return redirect('twf:collections')

    collection_item = CollectionItem.objects.get(id=collection_item_id)
    collection_item.status = status
    collection_item.save()
    messages.success(request, f"Collection item status set to '{status}'.")
    return redirect('twf:collection_item_edit', pk=collection_item_id)


def delete_collection(request, collection_id):
    """Delete a collection."""
    is_allowed = check_permission(request.user,
                                  "delete_collection",
                                  collection_id)
    if not is_allowed:
        messages.error(request, "You do not have permission to delete this collection.")
        return redirect('twf:collections')

    collection = Collection.objects.get(id=collection_id)

    workflows = Workflow.objects.filter(collection=collection)
    for workflow in workflows:
        print(f"Ending workflow {workflow.id}")
        workflow.finish(with_error=True)

    collection.delete()
    messages.success(request, "Collection deleted.")

    return redirect('twf:collections')


def fill_collection_item(item, page, skip_empty_types=False, structure_tag_filter_list=None):
    """Create a collection item."""
    if structure_tag_filter_list is None:
        structure_tag_filter_list = []

    annotations = page.get_annotations()
    for annotation in annotations:
        cleaned_annotation = clean_annotation(annotation)
        annotation_type = cleaned_annotation['type']

        if annotation_type == 'empty' and skip_empty_types:
            continue

        if annotation_type in structure_tag_filter_list:
            continue

        item.document_configuration['annotations'].append(cleaned_annotation)

def clean_annotation(annotation):
    """Clean an annotation."""
    cleaned_annotation = annotation.copy()
    if 'type' not in cleaned_annotation:
        cleaned_annotation['type'] = 'empty'
    if 'text' not in cleaned_annotation:
        cleaned_annotation['text'] = ''
    return cleaned_annotation