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
    messages.success(request, f"Tag {pk} has been parked.")

    return get_referrer_or_default(request, default="twf:tags_overview")


def park_all_identical_tags(request, pk):
    """Parks all tags with the same variation as the specified tag."""
    tag = get_object_or_404(PageTag, pk=pk)
    project = tag.page.document.project

    # Find all unparked tags with the same variation in the same project
    identical_tags = PageTag.objects.filter(
        page__document__project=project, variation=tag.variation, is_parked=False
    )

    count = identical_tags.count()

    # Park all identical tags
    for identical_tag in identical_tags:
        identical_tag.is_parked = True
        identical_tag.save(current_user=request.user)

    messages.success(
        request, f'Parked {count} tag(s) with variation "{tag.variation}".'
    )

    return get_referrer_or_default(request, default="twf:tags_overview")


def unpark_tag(request, pk):
    """Unparks a tag."""
    tag = get_object_or_404(PageTag, pk=pk)
    tag.is_parked = False
    tag.save(current_user=request.user)
    messages.success(request, f"Tag {pk} has been unparked.")

    return get_referrer_or_default(request, default="twf:tags_overview")


def ungroup_tag(request, pk):
    """Ungroups a tag."""
    tag = get_object_or_404(PageTag, pk=pk)
    tag.dictionary_entry = None
    tag.date_variation_entry = None
    tag.save(current_user=request.user)
    messages.success(request, f"Tag {pk} has been ungrouped.")

    return get_referrer_or_default(request, default="twf:tags_overview")


def delete_tag(request, pk):
    """Deletes a tag."""
    tag = get_object_or_404(PageTag, pk=pk)
    tag.delete()
    messages.success(request, f"Tag {pk} has been deleted.")

    return get_referrer_or_default(request, default="twf:tags_overview")
