from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

from twf.models import Dictionary
from twf.views.views_base import TWFView


def remove_dictionary_from_project(request, pk):
    """Remove a dictionary from the project."""
    dictionary = get_object_or_404(Dictionary, pk=pk)
    project = TWFView.s_get_project(request)
    project.selected_dictionaries.remove(dictionary)
    project.save(current_user=request.user)

    messages.success(request, f'Dictionary {dictionary.label} has been removed from your project.')

    # Get the HTTP referer URL
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)

    return redirect('twf:dictionaries')