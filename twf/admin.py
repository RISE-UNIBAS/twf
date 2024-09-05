"""Admin View configuration for the twf models."""
from django.contrib import admin
from .models import (
    UserProfile, Project, Document, Page, Dictionary, DictionaryEntry,
    Variation, PageTag, Collection, CollectionItem, DateVariation
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_filter = ['clearance_level', 'user']
    search_fields = ['user__username', 'user__email']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_filter = ['status', 'created_at', 'owner']
    search_fields = ['title', 'collection_id']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_filter = ['project', 'created_at']
    search_fields = ['title', 'document_id']

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_filter = ['document', 'document__document_id', 'tk_page_number', 'is_ignored']
    search_fields = ['tk_page_id', 'document__document_id']

@admin.register(Dictionary)
class DictionaryAdmin(admin.ModelAdmin):
    list_filter = ['type', 'created_at']
    search_fields = ['label']

@admin.register(DictionaryEntry)
class DictionaryEntryAdmin(admin.ModelAdmin):
    list_filter = ['dictionary', 'created_at']
    search_fields = ['label']

@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_filter = ['entry', 'created_at']
    search_fields = ['variation']

@admin.register(PageTag)
class PageTagAdmin(admin.ModelAdmin):
    list_filter = ['page', 'variation_type', 'is_parked']
    search_fields = ['variation']

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_filter = ['project', 'created_at']
    search_fields = ['title']

@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_filter = ['collection', 'created_at']
    search_fields = ['title', 'document__title']

@admin.register(DateVariation)
class DateVariationAdmin(admin.ModelAdmin):
    list_filter = ['created_at']
    search_fields = ['variation']

# Register all models without custom admin classes
# admin.site.register(UserProfile, UserProfileAdmin)
# admin.site.register(Project, ProjectAdmin)
# admin.site.register(Document, DocumentAdmin)
# admin.site.register(Page, PageAdmin)
# admin.site.register(Dictionary, DictionaryAdmin)
# admin.site.register(DictionaryEntry, DictionaryEntryAdmin)
# admin.site.register(Variation, VariationAdmin)
# admin.site.register(PageTag, PageTagAdmin)
# admin.site.register(Collection, CollectionAdmin)
# admin.site.register(CollectionItem, CollectionItemAdmin)
# admin.site.register(DateVariation, DateVariationAdmin)
