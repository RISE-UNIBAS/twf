"""Urls for the twf app."""
from django.urls import path
from django.contrib.auth import views as auth_views

from twf.tasks.task_status import task_status_view
from twf.tasks.task_triggers import start_task_creation, start_extraction, start_gnd_batch, start_geonames_batch, \
    start_wikidata_batch, start_openai_batch, start_gnd_request, start_geonames_request, start_wikidata_request, \
    start_openai_request, start_gemini_doc_batch, start_openai_doc_batch, start_claude_doc_batch
from twf.views.dictionaries.views_batches import TWFDictionaryGNDBatchView, TWFDictionaryGeonamesBatchView, \
    TWFDictionaryWikidataBatchView, TWFDictionaryOpenaiBatchView
from twf.views.dictionaries.views_requests import TWFDictionaryGNDRequestView, TWFDictionaryGeonamesRequestView, \
    TWFDictionaryWikidataRequestView, TWFDictionaryOpenaiRequestView
from twf.views.documents.views_documents import TWFDocumentsOverviewView, TWFDocumentsBrowseView, TWFDocumentCreateView, \
    TWFDocumentNameView, TWFDocumentDetailView
from twf.views.documents.views_documents_ai import TWFDocumentOpenAIBatchView, \
    TWFDocumentGeminiBatchView, TWFDocumentClaudeBatchView
from twf.views.home.views_home import TWFHomeView, TWFHomeLoginView, TWFHomePasswordChangeView, TWFHomeUserOverView, \
    TWFHomeUserManagementView, TWFSelectProjectView
from twf.views.project.views_project_setup import TWFProjectSetupView
from twf.views.views_ajax_download import ajax_transkribus_download_export, download_progress_view
from twf.views.views_ajax_export import ajax_transkribus_request_export, ajax_transkribus_request_export_status, \
    ajax_transkribus_reset_export
from twf.views.views_ajax_metadata import start_metadata_extraction, stream_metadata_extraction_progress
from twf.views.views_ajax_validation import validate_page_field, validate_document_field
from twf.views.dollections.views_collection import RemovePartView, SplitCollectionItemView, \
    UpdateCollectionItemView, TWFCollectionsView, TWFProjectCollectionsCreateView, \
    TWFProjectCollectionsDetailView, TWFProjectCollectionsReviewView, TWFProjectCollectionsAddDocumentView
from twf.views.views_command import park_tag, unpark_tag, ungroup_tag
from twf.views.dictionaries.views_dictionaries import TWFDictionaryOverviewView, TWFDictionaryDictionaryView, \
    delete_variation, TWFDictionaryDictionaryEditView, TWFDictionaryDictionaryEntryEditView, \
    TWFDictionaryDictionaryEntryView, TWFDictionaryImportView, \
    TWFDictionaryNormDataView, TWFDictionaryCreateView, skip_entry
from twf.views.export.views_export import TWFExportDocumentsView, TWFExportCollectionsView, TWFExportProjectView, \
    TWFExportOverviewView, TWFExportTagsView, TWFExportDictionariesView, TWFExportDictionaryView
from twf.views.metadata.views_metadata import TWFMetadataReviewDocumentsView, \
    TWFMetadataLoadDataView, TWFMetadataExtractTagsView, TWFMetadataReviewPagesView, TWFMetadataOverviewView, \
    TWFMetadataLoadSheetsDataView
from twf.views.project.views_project import select_project, \
    TWFProjectSettingsView, TWFProjectQueryView, TWFProjectOverviewView
from twf.views.project.views_project_ai import TWFProjectAIQueryView
from twf.views.tags.views_tags import TWFTagsView, TWFProjectTagsView, TWFProjectTagsOpenView, TWFProjectTagsParkedView, \
    TWFProjectTagsResolvedView, TWFProjectTagsIgnoredView, TWFTagsDatesView, TWFTagsGroupView, TWFTagsOverviewView, \
    TWFTagsExtractView

urlpatterns = [
    #############################
    # FRAMEWORK (HOME)
    path('', TWFHomeView.as_view(), name='home'),
    path('about/', TWFHomeView.as_view(template_name='twf/home/about.html'), name='about'),
    path('login/', TWFHomeLoginView.as_view(), name='login'),
    path('logout/confirm/',
         TWFHomeView.as_view(page_title='Logout', template_name='twf/home/users/logout.html'), name='user_logout'),
    path('user/change/password/', TWFHomePasswordChangeView.as_view(), name='user_change_password'),
    path('user/overview/', TWFHomeUserOverView.as_view(), name='user_overview'),
    path('user/management/', TWFHomeUserManagementView.as_view(), name='user_management'),
    path('logout/', auth_views.LogoutView.as_view(next_page='twf:home'), name='logout'),

    # Select Project
    path('project/select/<int:pk>/confirm/', TWFSelectProjectView.as_view(), name='project_select'),
    path('project/select/<int:pk>', select_project, name='project_do_select'),

    #############################
    # PROJECT

    # Project Data
    path('project/overview/', TWFProjectOverviewView.as_view(), name='project_overview'),
    path('project/setup/', TWFProjectSetupView.as_view(page_title='Project Setup'), name='project_setup'),
    path('project/setup/tk/export/',
         TWFProjectSetupView.as_view(template_name='twf/project/setup_export.html', page_title='Project TK Export'),
         name='project_tk_export'),
    path('project/setup/tk/structure/', TWFProjectSetupView.as_view(template_name='twf/project/setup_structure.html',
                                                                    page_title='Project TK Structure'),
         name='project_tk_structure'),
    path('project/setup/sheets/metadata/', TWFProjectSetupView.as_view(template_name='twf/project/setup_metadata.html',
                                                                       page_title='Project Sheets Metadata'),
         name='project_sheets_metadata'),
    path('project/settings/', TWFProjectSettingsView.as_view(), name='project_settings'),

    # Project options
    path('project/query/', TWFProjectQueryView.as_view(), name='project_query'),
    path('project/ai/query/', TWFProjectAIQueryView.as_view(), name='project_ai_query'),

    #############################
    # DOCUMENTS
    path('documents/', TWFDocumentsOverviewView.as_view(), name='documents_overview'),
    path('documents/browse/', TWFDocumentsBrowseView.as_view(), name='documents_browse'),
    path('documents/create/', TWFDocumentCreateView.as_view(), name='documents_create'),
    path('documents/name/', TWFDocumentNameView.as_view(), name='name_documents'),
    path('document/<int:pk>/', TWFDocumentDetailView.as_view(), name='view_document'),

    path('documents/batch/openai/', TWFDocumentOpenAIBatchView.as_view(), name='documents_batch_openai'),
    path('documents/batch/gemini/', TWFDocumentGeminiBatchView.as_view(), name='documents_batch_gemini'),
    path('documents/batch/claude/', TWFDocumentClaudeBatchView.as_view(), name='documents_batch_claude'),

    #############################
    # TAGS
    path('tags/overview/', TWFTagsOverviewView.as_view(), name='tags_overview'),
    path('tags/extract/', TWFTagsExtractView.as_view(), name='tags_extract'),
    path('tags/all/', TWFProjectTagsView.as_view(template_name='twf/tags/all_tags.html',
                                                 page_title='All Tags'),
         name='tags_all'),
    path('tags/settings/', TWFTagsView.as_view(template_name='twf/tags/settings.html'), name='tags_settings'),
    path('tags/group/', TWFTagsGroupView.as_view(), name='tags_group'),
    path('tags/dates/', TWFTagsDatesView.as_view(), name='tags_dates'),
    path('tags/view/parked/', TWFProjectTagsParkedView.as_view(), name='tags_view_parked'),
    path('tags/view/open/', TWFProjectTagsOpenView.as_view(), name='tags_view_open'),
    path('tags/view/resolved/', TWFProjectTagsResolvedView.as_view(), name='tags_view_resolved'),
    path('tags/view/ignored/', TWFProjectTagsIgnoredView.as_view(), name='tags_view_ignored'),
    path('tags/park/<int:pk>/', park_tag, name='tags_park'),
    path('tags/unpark/<int:pk>/', unpark_tag, name='tags_unpark'),
    path('tags/ungroup/<int:pk>/', ungroup_tag, name='tags_ungroup'),

    #############################
    # DICTIONARIES
    path('dictionaries/', TWFDictionaryOverviewView.as_view(), name='dictionaries'),
    path('dictionaries/create/', TWFDictionaryCreateView.as_view(), name='dictionary_create'),
    path('dictionaries/<int:pk>/', TWFDictionaryDictionaryView.as_view(), name='dictionaries_view'),
    path('dictionaries/<int:pk>/edit/', TWFDictionaryDictionaryEditView.as_view(), name='dictionaries_edit'),

    path('dictionaries/entry/<int:pk>/', TWFDictionaryDictionaryEntryView.as_view(), name='dictionaries_entry_view'),
    path('dictionaries/entry/<int:pk>/skip/', skip_entry, name='dictionaries_entry_skip'),
    path('dictionaries/entry/<int:pk>/edit/',
         TWFDictionaryDictionaryEntryEditView.as_view(), name='dictionaries_entry_edit'),
    path('dictionaries/import/', TWFDictionaryImportView.as_view(), name='dictionaries_import'),
    path('dictionaries/normalization/wizard/', TWFDictionaryNormDataView.as_view(), name='dictionaries_normalization'),
    path('dictionaries/variations/delete/<int:pk>/', delete_variation, name='delete_variation'),

    path('dictionaries/batch/gnd/', TWFDictionaryGNDBatchView.as_view(), name='dictionaries_batch_gnd'),
    path('dictionaries/batch/geonames/', TWFDictionaryGeonamesBatchView.as_view(), name='dictionaries_batch_geonames'),
    path('dictionaries/batch/wikidata/', TWFDictionaryWikidataBatchView.as_view(), name='dictionaries_batch_wikidata'),
    path('dictionaries/batch/openai/', TWFDictionaryOpenaiBatchView.as_view(), name='dictionaries_batch_openai'),

    path('dictionaries/request/gnd/', TWFDictionaryGNDRequestView.as_view(), name='dictionaries_request_gnd'),
    path('dictionaries/request/geonames/', TWFDictionaryGeonamesRequestView.as_view(), name='dictionaries_request_geonames'),
    path('dictionaries/request/wikidata/', TWFDictionaryWikidataRequestView.as_view(), name='dictionaries_request_wikidata'),
    path('dictionaries/request/openai/', TWFDictionaryOpenaiRequestView.as_view(), name='dictionaries_request_openai'),

    #############################
    # COLLECTIONS
    path('collections/', TWFCollectionsView.as_view(), name='collections'),
    path('project/collections/create/', TWFProjectCollectionsCreateView.as_view(), name='project_collections_create'),
    path('project/collections/<int:pk>/', TWFProjectCollectionsDetailView.as_view(), name='collections_view'),
    path('project/collections/review/<int:pk>/', TWFProjectCollectionsReviewView.as_view(),
         name='project_collection_review'),
    path('project/collections/item/<int:item_id>/remove_part/<int:part_id>/', RemovePartView.as_view(),
         name='project_collections_item_remove_part'),
    path('project/collections/item/<int:pk>/split/<int:part_id>/', SplitCollectionItemView.as_view(),
         name='project_collections_item_split'),

    path('collections/item/update/<int:pk>/', UpdateCollectionItemView.as_view(),
         name='project_collections_item_update'),

    path('project/collections/<int:pk>/add/document', TWFProjectCollectionsAddDocumentView.as_view(),
         name='project_collections_add_document'),


    #############################
    # EXPORT
    path('export/', TWFExportOverviewView.as_view(), name='export_overview'),
    path('export/documents/', TWFExportDocumentsView.as_view(), name='export_documents'),
    path('export/collections/', TWFExportCollectionsView.as_view(), name='export_collections'),
    path('export/project/', TWFExportProjectView.as_view(), name='export_project'),
    path('export/tags/', TWFExportTagsView.as_view(), name='export_tags'),

    path('export/dictionaries/', TWFExportDictionariesView.as_view(), name='export_dictionaries'),
    path('export/dictionaries/<int:pk>/', TWFExportDictionaryView.as_view(), name='export_dictionary'),


    #############################
    # CELERY TASKS
    path('celery/status/<str:task_id>/', task_status_view, name='celery_task_status'),

    path('celery/transkribus/extract/', start_extraction, name='task_transkribus_extract_export'),
    path('celery/transkribus/tags/extract/', start_task_creation, name='task_transkribus_extract_tags'),

    path('celery/documents/batch/openai/', start_openai_doc_batch, name='task_documents_batch_openai'),
    path('celery/documents/batch/gemini/', start_gemini_doc_batch, name='task_documents_batch_gemini'),
    path('celery/documents/batch/claude/', start_claude_doc_batch, name='task_documents_batch_claude'),

    path('celery/dictionaries/batch/gnd/', start_gnd_batch, name='task_dictionaries_batch_gnd'),
    path('celery/dictionaries/batch/geonames/', start_geonames_batch, name='task_dictionaries_batch_geonames'),
    path('celery/dictionaries/batch/wikidata/', start_wikidata_batch, name='task_dictionaries_batch_wikidata'),
    path('celery/dictionaries/batch/openai/', start_openai_batch, name='task_dictionaries_batch_openai'),

    path('celery/dictionaries/request/gnd/', start_gnd_request, name='task_dictionaries_request_gnd'),
    path('celery/dictionaries/request/geonames/', start_geonames_request, name='task_dictionaries_request_geonames'),
    path('celery/dictionaries/request/wikidata/', start_wikidata_request, name='task_dictionaries_request_wikidata'),
    path('celery/dictionaries/request/openai/', start_openai_request, name='task_dictionaries_request_openai'),

    #############################
    # AJAX CALLS
    path('ajax/transkribus/export/request/',
         ajax_transkribus_request_export, name='ajax_transkribus_request_export'),
    path('ajax/transkribus/export/reset/',
         ajax_transkribus_reset_export, name='ajax_transkribus_reset_export'),
    path('ajax/transkribus/export/status/',
         ajax_transkribus_request_export_status, name='ajax_transkribus_request_export__status'),
    path('ajax/transkribus/export/start/download/',
         ajax_transkribus_download_export, name='ajax_transkribus_download_export'),
    path('ajax/transkribus/export/monitor/download/',
         download_progress_view, name='download_progress'),


    path('ajax/transkribus/extract/metadata/', start_metadata_extraction,
         name='start_metadata_extraction'),
    path('ajax/transkribus/extract/metadata/monitor/', stream_metadata_extraction_progress,
         name='stream_metadata_extraction_progress'),


    #############################
    # METADATA
    path('metadata/overview/', TWFMetadataOverviewView.as_view(), name='metadata_overview'),

    path('metadata/load/metadata/', TWFMetadataLoadDataView.as_view(), name='metadata_load_metadata'),
    path('metadata/load/sheets/metadata/', TWFMetadataLoadSheetsDataView.as_view(), name='metadata_load_sheets_metadata'),
    path('metadata/extract/tags/', TWFMetadataExtractTagsView.as_view(), name='metadata_extract'),

    path('metadata/review/documents/', TWFMetadataReviewDocumentsView.as_view(), name='metadata_review_documents'),
    path('metadata/review/pages/', TWFMetadataReviewPagesView.as_view(), name='metadata_review_pages'),

    path('validate_page_field/', validate_page_field, name='validate_page_field'),
    path('validate_page_field/', validate_document_field, name='validate_document_field'),
]
