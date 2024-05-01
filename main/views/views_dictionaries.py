"""Views for the dictionary overview and the dictionary entries."""
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, ListView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from main.filters import DictionaryEntryFilter
from main.models import DictionaryEntry, Variation
from main.tables import DictionaryEntryTable
from main.views.views_base import BaseView


class DictionaryOverView(BaseView, TemplateView):
    """View for the dictionary overview."""
    template_name = 'main/dictionaries.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dictionaries'] = self.get_dictionaries()
        return context


class DictionaryView(SingleTableMixin, FilterView, ListView, BaseView):
    """View for the dictionary entries."""
    template_name = 'main/dictionary.html'
    table_class = DictionaryEntryTable
    model = DictionaryEntry
    filterset_class = DictionaryEntryFilter
    paginate_by = 10

    def get_queryset(self):
        """Get the queryset for the dictionary entries."""
        return DictionaryEntry.objects.filter(dictionary_id=self.kwargs.get('pk'))

    def get_context_data(self, **kwargs):
        """Add the dictionaries and the selected dictionary to the context."""
        context = super().get_context_data(**kwargs)
        context['dictionaries'] = self.get_dictionaries()
        context['dictionary'] = self.get_dictionaries().get(pk=self.kwargs.get('pk'))
        return context


class DictionaryEntryView(BaseView, TemplateView):
    """View for a single dictionary entry."""
    template_name = 'main/dictionary_entry.html'

    def get_context_data(self, **kwargs):
        """Add data to the context."""
        context = super().get_context_data(**kwargs)
        context['dictionaries'] = self.get_dictionaries()
        context['entry'] = DictionaryEntry.objects.get(pk=self.kwargs.get('pk'))
        return context


def delete_entry(request, pk):
    """Delete a dictionary entry."""
    entry = get_object_or_404(DictionaryEntry, pk=pk)
    entry.delete()
    messages.success(request, f'Dictionary entry {pk} has been deleted.')

    # Get the HTTP referer URL
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)

    return redirect('main:dictionary', pk=entry.dictionary.pk)


def delete_variation(request, pk):
    """Delete a variation."""
    variation = get_object_or_404(Variation, pk=pk)
    variation.delete()
    messages.success(request, f'Variation {pk} has been deleted.')

    # Get the HTTP referer URL
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)

    return redirect('main:dictionary', pk=variation.entry.dictionary.pk)
