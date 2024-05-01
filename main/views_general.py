from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

from main.forms import CreateDictionaryEntryForm
from main.models import Dictionary, PageTag, DictionaryEntry, Variation


def assign_tag(request, pk, entry_id):
    tag = get_object_or_404(PageTag, pk=pk)
    entry = get_object_or_404(DictionaryEntry, pk=entry_id)
    tag.dictionary_entry = entry
    tag.save()
    messages.success(request, f'Tag {pk} has been assigned to entry {entry_id}.')
    return redirect('main:project_group_tags', pk=tag.page.document.project.pk)


def assign_tag_to_new_entry(request, pk):
    if request.method == 'POST':
        form = CreateDictionaryEntryForm(request.POST)
        if form.is_valid():
            # Process the form data
            page_tag_id = request.POST.get('new_tag_id', '')
            dict_type = request.POST.get('new_dict_type', '')
            variation = request.POST.get('new_variation', '')

            # Create the database entry
            entry = DictionaryEntry(
                dictionary=Dictionary.objects.filter(type=dict_type).first(),
                label=form.cleaned_data['label'],
                notes=form.cleaned_data['notes']
            )
            entry.save()
            entry.variations.create(entry=entry, variation=variation)

            PageTag.objects.filter(pk=page_tag_id).update(dictionary_entry=entry)

            return redirect('main:project_group_tags_type', pk=pk, tag_type=dict_type)

    return redirect('main:project', pk=pk)


def assign_tag_by_variation(request, pk, variation_id):
    tag = get_object_or_404(PageTag, pk=pk)
    variation = get_object_or_404(Variation, pk=variation_id)
    tag.dictionary_entry = variation.entry
    tag.save()
    messages.success(request, f'Tag {pk} has been assigned to entry {variation.entry.label}.')
    return redirect('main:project_group_tags', pk=tag.page.document.project.pk)
