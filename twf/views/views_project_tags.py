""" Views for the tag assignment of dictionary entries. """
from django.contrib import messages
from django.views.generic import TemplateView

from twf.forms import CreateDictionaryEntryForm, AssignToEntryForm
from twf.models import PageTag, Dictionary, DictionaryEntry, Variation
from twf.views.views_base import BaseProjectView


class ProjectGroupWizardView(BaseProjectView, TemplateView):
    """View to assign tags to dictionary entries."""
    template_name = 'twf/wizard.html'

    def post(self, request, *args, **kwargs):
        """Handle the post request."""
        if 'create_new' in request.POST:
            new_entry_label = request.POST.get('new_entry_label', None)
            if new_entry_label:
                tag_to_assign = PageTag.objects.get(pk=request.POST.get('tag_id', None))
                dictionary = Dictionary.objects.get(pk=request.POST.get('dictionary_id', None))
                new_entry = DictionaryEntry(dictionary=dictionary, label=new_entry_label,
                                            notes=self.request.POST.get('notes_on_entry', ''))
                new_entry.save(current_user=self.request.user)

                variation = Variation(entry=new_entry, variation=tag_to_assign.variation)
                variation.save(current_user=self.request.user)
                tag_to_assign.dictionary_entry = new_entry
                tag_to_assign.save(current_user=self.request.user)

                self.save_other_tags(tag_to_assign, new_entry, self.request.user)

                messages.success(request, 'New entry created: ' + new_entry_label)
            else:
                messages.error(request, 'Please provide a label for the new entry.')
        if 'add_to_existing' in request.POST:
            selected_entry = request.POST.get('selected_entry', None)
            if selected_entry:
                self.add_variation_to_entry(selected_entry, request.POST.get('tag_id', ''), self.request.user)
            else:
                messages.error(request, 'Please select an entry to add the tag to.')
        else:
            for key in request.POST.keys():
                if key.startswith('add_to_'):
                    selected_entry = key.replace('add_to_', '')
                    if selected_entry:
                        self.add_variation_to_entry(selected_entry, request.POST.get('tag_id', ''), self.request.user)
                    else:
                        messages.error(request, 'Please select an entry to add the tag to.')

        return super().get(request, *args, **kwargs)

    def add_variation_to_entry(self, entry_id, tag_id, user):
        """Add a variation to an existing dictionary entry."""
        try:
            entry = DictionaryEntry.objects.get(pk=entry_id)
            tag = PageTag.objects.get(pk=tag_id)
            variation = Variation(entry=entry, variation=tag.variation)
            variation.save(current_user=user)
            tag.dictionary_entry = entry
            tag.save(current_user=user)

            self.save_other_tags(tag, entry, user)

            messages.success(self.request, 'Variation added to entry: ' + entry.label)
        except DictionaryEntry.DoesNotExist:
            messages.error(self.request, 'Entry does not exist: ' + entry_id)

    @staticmethod
    def save_other_tags(tag, entry, user):
        """Save all other tags of the same variation to the same dictionary entry."""
        other_tags = PageTag.objects.filter(variation=tag.variation, dictionary_entry=None)
        for other_tag in other_tags:
            other_tag.dictionary_entry = entry
            other_tag.save(current_user=user)

    def get_context_data(self, **kwargs):
        """Add the tag to the context."""
        # Determine which group of tags to show
        tag_types = self.get_tag_types()
        if self.request.GET.get('tag_type', None):
            tag_type = self.request.GET.get('tag_type')
        else:
            tag_type = tag_types[0]

        # Translate the tag type to the dictionary type
        dict_type = tag_type
        if tag_type in self.get_project().tag_type_translator:
            dict_type = self.get_project().tag_type_translator[tag_type]

        # Get an unassigned tag from the selected group
        unassigned_tag = PageTag.objects.filter(page__document__project=self.get_project(),
                                                dictionary_entry=None,
                                                variation_type=tag_type,
                                                is_parked=False).exclude(
            variation_type__in=self.get_excluded_types()).distinct('variation').first()

        # Create the context
        context = super().get_context_data(**kwargs)

        # Add: All tag types which can be assigned (To select the group) and the selected group
        context['tag_types'] = tag_types
        context['selected_type'] = tag_type

        # Add: The tag which should be assigned and its closest variations
        context['tag'] = {'tag': unassigned_tag,
                          'closest': unassigned_tag.get_closest_variations()}

        # Add: The dictionary type and id to assign the tag to
        context['dict_type'] = dict_type
        try:
            dict_of_type = Dictionary.objects.get(type=dict_type)
        except Dictionary.DoesNotExist:
            dict_of_type = Dictionary(label=dict_type, type=dict_type)
            dict_of_type.save(current_user=self.request.user)
            messages.warning(self.request, f'Created new dictionary for type: {dict_type}')
        context['dict_id'] = dict_of_type.id

        # Add: All variations of the selected dictionary type
        all_variations = DictionaryEntry.objects.filter(dictionary__type=dict_type)
        context['variations'] = all_variations

        return context


class ProjectGroupTagsView(BaseProjectView, TemplateView):
    """View to assign tags to dictionary entries."""
    template_name = 'twf/structure.html'

    def get_unassigned_tag_blocks(self):
        """Get all unassigned tags grouped by tag type."""
        blocks = []
        unassigned_tags = PageTag.objects.filter(page__document__project=self.get_project(),
                                                 dictionary_entry=None,
                                                 is_parked=False,
                                                 variation_type=self.kwargs.get('tag_type'))

        variation_types = unassigned_tags.values_list('variation_type', flat=True).order_by('variation_type').distinct()
        for v_type in variation_types:
            dict_type = v_type
            if v_type in self.get_project().tag_type_translator:
                dict_type = self.get_project().tag_type_translator[v_type]
            block = {
                'type': v_type,
                'dict_type': dict_type,
                'tags': unassigned_tags.filter(variation_type=v_type).order_by('variation')[:250]
            }
            blocks.append(block)
        return blocks

    def get_context_data(self, **kwargs):
        """Add the tag to the context."""
        context = super().get_context_data(**kwargs)
        context['tag_type'] = self.kwargs.get('tag_type', None)
        context['project'] = self.get_project()
        context['unassigned_tags'] = self.get_unassigned_tag_blocks()
        context['create_form'] = CreateDictionaryEntryForm()
        context['add_to_form'] = AssignToEntryForm(tag_type=self.kwargs.get('tag_type', None))
        return context


class ProjectParkedTagsView(BaseProjectView, TemplateView):
    """View to display all parked tags."""
    template_name = 'twf/parked.html'

    def get_parked_tags(self):
        """Get all parked tags."""
        return PageTag.objects.filter(page__document__project=self.get_project(),
                                      dictionary_entry=None,
                                      is_parked=True).exclude(variation_type__in=['date', 'print_date'])

    def get_context_data(self, **kwargs):
        """Add the parked tags to the context."""
        context = super().get_context_data(**kwargs)
        context['parked'] = self.get_parked_tags()
        return context


class ProjectSpecialTagsView(BaseProjectView, TemplateView):
    """View to display all special tags."""
    template_name = 'twf/special.html'

    def get_special_tags(self):
        """Get all special tags."""
        return PageTag.objects.filter(page__document__project=self.get_project(),
                                      dictionary_entry=None,
                                      variation_type__in=['date', 'print_date'],
                                      is_parked=False)[:200]

    def get_context_data(self, **kwargs):
        """Add the special tags to the context."""
        context = super().get_context_data(**kwargs)
        context['special'] = self.get_special_tags()
        return context
