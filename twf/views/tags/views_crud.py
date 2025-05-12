"""Views for command actions."""
from django.contrib import messages
from django.shortcuts import get_object_or_404

from twf.models import PageTag
from twf.views.views_base import get_referrer_or_default


def park_tag(request, pk):
    """Parks a tag."""
    tag = get_object_or_404(PageTag, pk=pk)
    tag.is_parked = True
    tag.save(current_user=request.user)
    messages.success(request, f'Tag {pk} has been parked.')

    return get_referrer_or_default(request, default='twf:tags_overview')


def unpark_tag(request, pk):
    """Unparks a tag."""
    tag = get_object_or_404(PageTag, pk=pk)
    tag.is_parked = False
    tag.save(current_user=request.user)
    messages.success(request, f'Tag {pk} has been unparked.')

    return get_referrer_or_default(request, default='twf:tags_overview')



def ungroup_tag(request, pk):
    """Ungroups a tag."""
    tag = get_object_or_404(PageTag, pk=pk)
    tag.dictionary_entry = None
    tag.date_variation_entry = None
    tag.save(current_user=request.user)
    messages.success(request, f'Tag {pk} has been ungrouped.')

    return get_referrer_or_default(request, default='twf:tags_overview')


def delete_tag(request, pk):
    """Deletes a tag."""
    tag = get_object_or_404(PageTag, pk=pk)
    tag.delete()
    messages.success(request, f'Tag {pk} has been deleted.')

    return get_referrer_or_default(request, default='twf:tags_overview')
