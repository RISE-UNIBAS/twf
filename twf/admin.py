"""Admin View configuration for the twf models."""
from django.contrib import admin
from .models import UserProfile, Project, Document, Page, Dictionary, DictionaryEntry, Variation, PageTag

admin.site.register(UserProfile)
admin.site.register(Project)
admin.site.register(Document)
admin.site.register(Page)
admin.site.register(Dictionary)
admin.site.register(DictionaryEntry)
admin.site.register(Variation)
admin.site.register(PageTag)
