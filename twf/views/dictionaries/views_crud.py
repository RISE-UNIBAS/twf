from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

from twf.models import Dictionary, DictionaryEntry, PageTag, Variation
from twf.tasks.instant_tasks import save_instant_task_add_dictionary
from twf.views.views_base import TWFView, get_referrer_or_default


def remove_dictionary_from_project(request, pk):
    """Remove a dictionary from the project."""
    dictionary = get_object_or_404(Dictionary, pk=pk)
    project = TWFView.s_get_project(request)
    project.selected_dictionaries.remove(dictionary)
    project.save(current_user=request.user)

    messages.success(request, f'Dictionary {dictionary.label} has been removed from your project.')

    return get_referrer_or_default(request, default='twf:dictionaries')


def delete_variation(request, pk):
    """Delete a variation."""
    variation = get_object_or_404(Variation, pk=pk)

    all_page_tags = PageTag.objects.filter(variation=variation)
    for page_tag in all_page_tags:
        page_tag.dictionary_entry = None
        page_tag.save()

    variation.delete()
    messages.success(request, f'Variation {pk} has been deleted.')

    return get_referrer_or_default(request, default='twf:dictionaries')


def delete_entry(request, pk):
    """Delete a dictionary entry."""
    entry = get_object_or_404(DictionaryEntry, pk=pk)
    entry.delete()
    messages.success(request, f'Dictionary entry {pk} has been deleted.')

    return get_referrer_or_default(request, default='twf:dictionaries')


def skip_entry(request, pk):
    """Skip a dictionary entry."""
    entry = get_object_or_404(DictionaryEntry, pk=pk)
    entry.save(current_user=request.user)
    messages.success(request, f'Dictionary entry {pk} has been skipped.')

    return get_referrer_or_default(request, default='twf:dictionaries')


def add_dictionary_to_project(request, pk):
    """Add a dictionary to the project."""
    dictionary = get_object_or_404(Dictionary, pk=pk)
    project = TWFView.s_get_project(request)
    project.selected_dictionaries.add(dictionary)
    project.save(current_user=request.user)

    save_instant_task_add_dictionary(project,
                                     request.user,
                                     f"Added dictionary {dictionary.label} to project")

    messages.success(request, f'Dictionary {dictionary.label} has been added to your project.')

    return get_referrer_or_default(request, default='twf:dictionaries')


def delete_dictionary_entry(request, pk):
    """Delete a dictionary entry."""
    entry = get_object_or_404(DictionaryEntry, pk=pk)
    entry.delete()
    messages.success(request, f'Dictionary entry {pk} has been deleted.')

    return get_referrer_or_default(request, default='twf:dictionaries')