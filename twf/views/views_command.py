"""Views for command actions."""
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect

from twf.models import PageTag


def park_tag(request, pk):
    """Parks a tag."""
    tag = get_object_or_404(PageTag, pk=pk)
    tag.is_parked = True
    tag.save()
    messages.success(request, f'Tag {pk} has been parked.')

    # Get the HTTP referer URL
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)

    return redirect('twf:project_group_tags', pk=tag.page.document.project.pk)


def unpark_tag(request, pk):
    """Unparks a tag."""
    tag = get_object_or_404(PageTag, pk=pk)
    tag.is_parked = False
    tag.save()
    messages.success(request, f'Tag {pk} has been unparked.')

    # Get the HTTP referer URL
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)

    return redirect('twf:project_group_tags', pk=tag.page.document.project.pk)
