"""Urls for the twf app."""
from django.urls import path
from django.contrib.auth import views as auth_views

from twf.tasks.task_status import task_status_view
from twf.views.views_ajax_download import ajax_transkribus_download_export, download_progress_view
from twf.views.views_ajax_export import ajax_transkribus_request_export, ajax_transkribus_request_export_status, \
    ajax_transkribus_reset_export
from twf.views.views_ajax_extract import start_extraction, stream_extraction_progress, stream_extraction_progress_detail
from twf.views.views_ajax_metadata import start_metadata_extraction, stream_metadata_extraction_progress
from twf.views.views_ajax_validation import validate_page_field, validate_document_field
from twf.views.views_base import TWFHomeView, TWFHomeLoginView, TWFHomePasswordChangeView, TWFHomeUserOverView, \
    TWFHomeUserManagementView
from twf.views.views_collection import RemovePartView, SplitCollectionItemView, \
    UpdateCollectionItemView, TWFProjectCollectionsView, TWFProjectCollectionsCreateView, \
    TWFProjectCollectionsDetailView, TWFProjectCollectionsReviewView, TWFProjectCollectionsAddDocumentView
from twf.views.views_command import park_tag, unpark_tag, ungroup_tag
from twf.views.views_dictionaries import TWFDictionaryView, TWFDictionaryOverviewView, TWFDictionaryDictionaryView, \
    delete_variation, TWFDictionaryDictionaryEditView, TWFDictionaryDictionaryEntryEditView, \
    TWFDictionaryDictionaryEntryView, TWFDictionaryImportView, TWFDictionaryDictionaryExportView, \
    TWFDictionaryBatchGeonamesView, TWFDictionaryNormDataView, TWFDictionaryCreateView, skip_entry
from twf.views.views_export import TWFExportDataView
from twf.views.views_metadata import TWFMetadataReviewDocumentsView, \
    TWFMetadataLoadDataView, TWFMetadataExtractTagsView, TWFMetadataReviewPagesView, TWFMetadataOverviewView
from twf.views.views_project import TWFSelectProjectView, select_project, TWFProjectView, TWFProjectDocumentsView, \
    TWFProjectSettingsView, TWFProjectSetupView, TWFProjectDocumentView, TWFProjectQueryView, TWFProjectOverviewView, \
    TWFProjectDocumentCreateView, TWFProjectDocumentNameView
from twf.views.views_project_ai import TWFProjectAIBatchView, TWFProjectAIQueryView
from twf.views.views_tags import TWFTagsView, TWFProjectTagsView, TWFProjectTagsOpenView, TWFProjectTagsParkedView, \
    TWFProjectTagsResolvedView, TWFProjectTagsIgnoredView, TWFTagsDatesView, TWFTagsGroupView, TWFTagsOverviewView

urlpatterns = [
    #############################
    # FRAMEWORK
    path('', TWFHomeView.as_view(),
         name='home'),
    path('login/', TWFHomeLoginView.as_view(),
         name='login'),
    path('logout/confirm/', TWFHomeView.as_view(page_title='Logout', template_name='twf/users/logout.html'),
         name='user_logout'),
    path('user/change/password/', TWFHomePasswordChangeView.as_view(),
         name='user_change_password'),
    path('user/overview/', TWFHomeUserOverView.as_view(),
         name='user_overview'),
    path('user/management/', TWFHomeUserManagementView.as_view(),
         name='user_management'),
    path('logout/', auth_views.LogoutView.as_view(next_page='twf:home'),
         name='logout'),

    #############################
    # PROJECT
    path('project/select/<int:pk>/confirm/', TWFSelectProjectView.as_view(),
         name='project_select'),
    path('project/select/<int:pk>', select_project,
         name='project_do_select'),
    path('project/overview/', TWFProjectOverviewView.as_view(),
         name='project_overview'),
    path('project/setup/', TWFProjectSetupView.as_view(page_title='Project Setup'),
         name='project_setup'),
    path('project/setup/tk/export/', TWFProjectSetupView.as_view(template_name='twf/project/setup_export.html',
                                                                 page_title='Project TK Export'),
         name='project_tk_export'),
    path('project/setup/tk/structure/', TWFProjectSetupView.as_view(template_name='twf/project/setup_structure.html',
                                                                    page_title='Project TK Structure'),
         name='project_tk_structure'),
    path('project/setup/sheets/metadata/', TWFProjectSetupView.as_view(template_name='twf/project/setup_metadata.html',
                                                                       page_title='Project Sheets Metadata'),
         name='project_sheets_metadata'),
    path('project/settings/', TWFProjectSettingsView.as_view(),
         name='project_settings'),
    path('project/export/', TWFExportDataView.as_view(),
         name='project_export'),
    path('project/query/', TWFProjectQueryView.as_view(),
         name='project_query'),
    path('project/ai/query/', TWFProjectAIQueryView.as_view(),
         name='project_ai_query'),

    path('project/batch/openai/', TWFProjectAIBatchView.as_view(),
         name='project_batch_openai'),
    path('project/batch/openai/ask-chatgpt/', TWFProjectAIBatchView.as_view(), name='project_batch_openai_ask-chatgpt'),

    #############################
    # DOCUMENTS
    path('project/documents/', TWFProjectDocumentsView.as_view(),
         name='project_documents'),
    path('project/documents/create/', TWFProjectDocumentCreateView.as_view(),
         name='create_document'),
    path('project/documents/name/', TWFProjectDocumentNameView.as_view(),
         name='name_documents'),
    path('project/document/<int:pk>/', TWFProjectDocumentView.as_view(),
         name='view_document'),

    #############################
    # COLLECTIONS
    path('project/collections/', TWFProjectCollectionsView.as_view(),
         name='project_collections'),
    path('project/collections/create/', TWFProjectCollectionsCreateView.as_view(),
         name='project_collections_create'),
    path('project/collections/<int:pk>/', TWFProjectCollectionsDetailView.as_view(),
         name='project_collections_view'),

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
    # TAGS
    path('tags/overview/', TWFTagsOverviewView.as_view(),
         name='tags_overview'),
    path('tags/all/', TWFProjectTagsView.as_view(template_name='twf/tags/all_tags.html',
                                                 page_title='All Tags'),
         name='tags_all'),
    path('tags/settings/', TWFTagsView.as_view(template_name='twf/tags/settings.html'),
         name='tags_settings'),
    path('tags/group/', TWFTagsGroupView.as_view(),
         name='tags_group'),
    path('tags/dates/', TWFTagsDatesView.as_view(),
         name='tags_dates'),
    path('tags/view/parked/', TWFProjectTagsParkedView.as_view(),
         name='tags_view_parked'),
    path('tags/view/open/', TWFProjectTagsOpenView.as_view(),
         name='tags_view_open'),
    path('tags/view/resolved/', TWFProjectTagsResolvedView.as_view(),
         name='tags_view_resolved'),
    path('tags/view/ignored/', TWFProjectTagsIgnoredView.as_view(),
         name='tags_view_ignored'),
    path('tags/park/<int:pk>/', park_tag,
         name='tags_park'),
    path('tags/unpark/<int:pk>/', unpark_tag,
         name='tags_unpark'),
    path('tags/ungroup/<int:pk>/', ungroup_tag,
         name='tags_ungroup'),

    #############################
    # DICTIONARIES
    path('dictionaries/', TWFDictionaryOverviewView.as_view(),
         name='dictionaries'),
    path('dictionaries/create/', TWFDictionaryCreateView.as_view(),
         name='dictionary_create'),
    path('dictionaries/<int:pk>/', TWFDictionaryDictionaryView.as_view(),
         name='dictionaries_view'),
    path('dictionaries/<int:pk>/edit/', TWFDictionaryDictionaryEditView.as_view(),
         name='dictionaries_edit'),
    path('dictionaries/<int:pk>/export/', TWFDictionaryDictionaryExportView.as_view(),
         name='dictionaries_export'),
    path('dictionaries/entry/<int:pk>/', TWFDictionaryDictionaryEntryView.as_view(),
         name='dictionaries_entry_view'),
    path('dictionaries/entry/<int:pk>/skip/', skip_entry,
         name='dictionaries_entry_skip'),
    path('dictionaries/entry/<int:pk>/edit/', TWFDictionaryDictionaryEntryEditView.as_view(),
         name='dictionaries_entry_edit'),
    path('dictionaries/import/', TWFDictionaryImportView.as_view(),
         name='dictionaries_import'),
    path('dictionaries/normalization/wizard/', TWFDictionaryNormDataView.as_view(),
         name='dictionaries_normalization'),
    path('dictionaries/variations/delete/<int:pk>/', delete_variation,
         name='delete_variation'),

    path('dictionaries/batch/gnd/', TWFDictionaryView.as_view(template_name='twf/dictionaries/batches/gnd.html',
                                                              page_title='Batch GND'),
         name='dictionaries_batch_gnd'),
    path('dictionaries/batch/geonames/', TWFDictionaryBatchGeonamesView.as_view(),
         name='dictionaries_batch_geonames'),
    path('dictionaries/batch/wikidata/',
         TWFDictionaryView.as_view(template_name='twf/dictionaries/batches/wikidata.html',
                                   page_title='Batch Wikidata'),
         name='dictionaries_batch_wikidata'),
    path('dictionaries/batch/openai/', TWFDictionaryView.as_view(template_name='twf/dictionaries/batches/openai.html',
                                                                 page_title='Batch Manual'),
         name='dictionaries_batch_openai'),


    #############################
    # AJAX CALLS
    path('ajax/transkribus/export/request/', ajax_transkribus_request_export, name='ajax_transkribus_request_export'),
    path('ajax/transkribus/export/reset/', ajax_transkribus_reset_export, name='ajax_transkribus_reset_export'),
    path('ajax/transkribus/export/status/', ajax_transkribus_request_export_status,
         name='ajax_transkribus_request_export__status'),
    path('ajax/transkribus/export/start/download/', ajax_transkribus_download_export,
         name='ajax_transkribus_download_export'),
    path('ajax/transkribus/export/monitor/download/', download_progress_view, name='download_progress'),
    path('ajax/transkribus/extract/', start_extraction, name='extract_and_process_zip'),
    path('ajax/transkribus/extract/metadata/', start_metadata_extraction,
         name='start_metadata_extraction'),
    path('ajax/transkribus/extract/monitor/', stream_extraction_progress,
         name='stream_extraction_progress'),
    path('ajax/transkribus/extract/monitor/details/', stream_extraction_progress_detail,
         name='stream_extraction_progress_detail'),
    path('ajax/transkribus/extract/metadata/monitor/', stream_metadata_extraction_progress,
         name='stream_metadata_extraction_progress'),
    path('celery/status/<str:task_id>/', task_status_view, name='celery_task_status'),

    #############################
    # METADATA
    path('metadata/overview/', TWFMetadataOverviewView.as_view(), name='metadata_overview'),

    path('metadata/load/metadata/', TWFMetadataLoadDataView.as_view(), name='metadata_load_metadata'),
    path('metadata/extract/tags/', TWFMetadataExtractTagsView.as_view(), name='metadata_extract'),

    path('metadata/review/documents/', TWFMetadataReviewDocumentsView.as_view(), name='metadata_review_documents'),
    path('metadata/review/pages/', TWFMetadataReviewPagesView.as_view(), name='metadata_review_pages'),

    path('validate_page_field/', validate_page_field, name='validate_page_field'),
    path('validate_page_field/', validate_document_field, name='validate_document_field'),
]
