"""Urls for the twf app."""
from django.urls import path
from django.contrib.auth import views as auth_views

from twf.tasks.task_status import task_status_view, task_cancel_view, task_remove_view
from twf.tasks.task_triggers import *
from twf.views.ajax.views_ajax_field_validation import validate_page_field, validate_document_field
from twf.views.ajax.views_ajax_markdown import ajax_markdown_generate, ajax_markdown_preview
from twf.views.ajax.views_ajax_prompts import load_prompt, save_prompt, get_prompts
from twf.views.ajax.views_ajax_transkribus_export import ajax_transkribus_request_export, \
    ajax_transkribus_reset_export, ajax_transkribus_request_export_status
from twf.views.collections.views_collections_ai import TWFCollectionsOpenaiBatchView, TWFCollectionsGeminiBatchView, \
    TWFCollectionsClaudeBatchView, TWFCollectionsOpenaiRequestView, TWFCollectionsGeminiRequestView, \
    TWFCollectionsClaudeRequestView
from twf.views.collections.views_crud import delete_collection, set_col_item_status_open, set_col_item_status_reviewed, \
    set_col_item_status_faulty, split_collection_item, copy_collection_item, delete_collection_item_annotation, \
    delete_collection_item, download_collection_item_txt, download_collection_item_json
from twf.views.dictionaries.views_dictionaries_ai import TWFDictionaryGNDBatchView, TWFDictionaryGeonamesBatchView, \
    TWFDictionaryWikidataBatchView, TWFDictionaryOpenaiBatchView, TWFDictionaryClaudeBatchView, \
    TWFDictionaryGeminiBatchView, TWFDictionaryGNDRequestView, TWFDictionaryGeonamesRequestView, \
    TWFDictionaryWikidataRequestView, TWFDictionaryOpenaiRequestView, TWFDictionaryClaudeRequestView, \
    TWFDictionaryGeminiRequestView
from twf.views.dictionaries.views_crud import remove_dictionary_from_project, add_dictionary_to_project, skip_entry, \
    delete_variation
from twf.views.documents.views_documents import TWFDocumentsOverviewView, TWFDocumentsBrowseView, \
    TWFDocumentCreateView, TWFDocumentNameView, TWFDocumentDetailView, TWFDocumentReviewView
from twf.views.documents.views_documents_ai import TWFDocumentOpenAIBatchView, \
    TWFDocumentGeminiBatchView, TWFDocumentClaudeBatchView, TWFDocumentOpenAIPageBatchView, \
    TWFDocumentGeminiPageBatchView, TWFDocumentClaudePageBatchView
from twf.views.export.views_crud import delete_export
from twf.views.home.views_home import TWFHomeView, TWFHomeLoginView, TWFHomePasswordChangeView, TWFHomeUserOverView, \
    TWFSelectProjectView, TWFHomeUserProfileView, TWFCreateProjectView, TWFManageProjectsView, TWFManageUsersView
from twf.views.metadata.views_metadata_ai import TWFMetadataLoadDataView, TWFMetadataLoadSheetsDataView
from twf.views.project.views_crud import delete_all_documents, delete_all_tags, delete_all_collections, select_project, \
    delete_project, close_project, delete_prompt
from twf.views.project.views_project_setup import TWFProjectSetupView, TWFProjectTranskribusExtractView
from twf.views.ajax.views_ajax_download import ajax_transkribus_download_export, download_progress_view
from twf.views.collections.views_collections import TWFCollectionsReviewView, TWFCollectionOverviewView, \
    TWFCollectionsCreateView, TWFCollectionsDetailView, TWFCollectionsEditView, TWFCollectionsAddDocumentView, \
    TWFCollectionItemEditView, TWFCollectionItemView, TWFCollectionListView
from twf.views.views_base import help_content
from twf.views.tags.views_crud import park_tag, unpark_tag, ungroup_tag
from twf.views.dictionaries.views_dictionaries import TWFDictionaryOverviewView, TWFDictionaryDictionaryView, \
    TWFDictionaryDictionaryEditView, TWFDictionaryDictionaryEntryEditView, TWFDictionaryDictionaryEntryView, \
    TWFDictionaryNormDataView, TWFDictionaryCreateView, TWFDictionaryDictionariesView, \
    TWFDictionaryAddView, TWFDictionaryMergeEntriesView
from twf.views.export.views_export import TWFExportDocumentsView, TWFExportCollectionsView, TWFExportProjectView, \
    TWFExportOverviewView, TWFExportTagsView, TWFExportDictionariesView, TWFImportDictionaryView, \
    TWFExportConfigurationView, TWFExportZenodoView, TWFExportListView
from twf.views.metadata.views_metadata import TWFMetadataReviewDocumentsView, TWFMetadataExtractTagsView, \
    TWFMetadataReviewPagesView, TWFMetadataOverviewView
from twf.views.project.views_project import TWFProjectQueryView, TWFProjectOverviewView, \
    TWFProjectTaskMonitorView, TWFProjectGeneralSettingsView, TWFProjectCredentialsSettingsView, \
    TWFProjectPromptsView, TWFProjectTaskSettingsView, TWFProjectExportSettingsView, TWFProjectCopyView, \
    TWFProjectResetView, TWFProjectUserManagementView, TWFProjectRepositorySettingsView, TWFProjectPromptEditView
from twf.views.project.views_project_ai import TWFProjectAIQueryView, TWFProjectGeminiQueryView, \
    TWFProjectClaudeQueryView
from twf.views.tags.views_tags import TWFProjectTagsView, TWFProjectTagsOpenView, \
    TWFProjectTagsParkedView, TWFProjectTagsResolvedView, TWFProjectTagsIgnoredView, TWFTagsDatesGroupView, \
    TWFTagsGroupView, TWFTagsOverviewView, TWFTagsExtractView, TWFTagsSettingsView
from twf.workflows.collection_workflows import start_review_collection_workflow
from twf.workflows.document_workflows import start_review_document_workflow

urlpatterns = [
    #############################
    # FRAMEWORK (HOME)
    path('', TWFHomeView.as_view(), name='home'),
    path('about/', TWFHomeView.as_view(template_name='twf/home/about.html'), name='about'),
    path('login/', TWFHomeLoginView.as_view(), name='login'),
    path('logout/confirm/',
         TWFHomeView.as_view(page_title='Logout', template_name='twf/home/users/logout.html'), name='user_logout'),
    path('user/profile/', TWFHomeUserProfileView.as_view(), name='user_profile'),
    path('user/change/password/', TWFHomePasswordChangeView.as_view(), name='user_change_password'),
    path('user/overview/', TWFHomeUserOverView.as_view(), name='user_overview'),
    path('logout/', auth_views.LogoutView.as_view(next_page='twf:home'), name='logout'),
    path('help/<str:view_name>/', help_content, name='help'),
    path('user/management/', TWFManageUsersView.as_view(), name='twf_user_management'),

    # Select Project
    path('project/select/<int:pk>/confirm/', TWFSelectProjectView.as_view(), name='project_select'),
    path('project/select/<int:pk>', select_project, name='project_do_select'),
    path('project/create/', TWFCreateProjectView.as_view(), name='project_create'),
    path('projects/manage/', TWFManageProjectsView.as_view(), name='project_management'),
    path('project/delete/<int:pk>', delete_project, name='project_do_delete'),
    path('project/close/<int:pk>', close_project, name='project_do_close'),

    #############################
    # PROJECT
    path('project/overview/', TWFProjectOverviewView.as_view(), name='project_overview'),
    path('project/setup/', TWFProjectSetupView.as_view(template_name='twf/project/setup/setup.html',
                                                       page_title='Project Setup'), name='project_setup'),
    path('project/setup/tk/export/',
         TWFProjectSetupView.as_view(template_name='twf/project/setup/setup_export.html',
                                     page_title='Project TK Export'), name='project_tk_export'),
    path('project/setup/tk/structure/', TWFProjectTranskribusExtractView.as_view(), name='project_tk_structure'),
    path('project/setup/tk/test/', TWFProjectSetupView.as_view(template_name='twf/project/setup/test_export.html',
                                                               page_title='Test Transkribus Export'),
         name='project_test_export'),
    path('project/setup/copy/', TWFProjectCopyView.as_view(), name='project_copy'),
    path('project/setup/reset/', TWFProjectResetView.as_view(), name='project_reset'),
    path('project/setup/reset/delete/documents/', delete_all_documents, name='reset_remove_all_documents'),
    path('project/setup/reset/delete/tags/', delete_all_tags, name='reset_remove_all_tags'),
    path('project/setup/reset/delete/collections/', delete_all_collections, name='reset_remove_all_collections'),

    path('project/task/monitor/', TWFProjectTaskMonitorView.as_view(), name='project_task_monitor'),
    path('project/prompts/', TWFProjectPromptsView.as_view(), name='project_prompts'),
    path('project/prompts/delete/<int:pk>/', delete_prompt, name='project_delete_prompt'),
    path('project/prompts/edit/<int:pk>/', TWFProjectPromptEditView.as_view(), name='project_edit_prompt'),

    path('project/settings/general/', TWFProjectGeneralSettingsView.as_view(), name='project_settings_general'),
    path('project/settings/credentials/', TWFProjectCredentialsSettingsView.as_view(),
         name='project_settings_credentials'),
    path('project/settings/tasks/', TWFProjectTaskSettingsView.as_view(), name='project_settings_tasks'),
    path('project/settings/export/', TWFProjectExportSettingsView.as_view(), name='project_settings_export'),
    path('project/settings/repositories/', TWFProjectRepositorySettingsView.as_view(),
         name='project_settings_repository'),
    path('project/user/management/', TWFProjectUserManagementView.as_view(), name='user_management'),

    # Project options
    path('project/query/', TWFProjectQueryView.as_view(), name='project_query'),
    path('project/openai/query/', TWFProjectAIQueryView.as_view(), name='project_ai_query'),
    path('project/gemini/query/', TWFProjectGeminiQueryView.as_view(), name='project_gemini_query'),
    path('project/claude/query/', TWFProjectClaudeQueryView.as_view(), name='project_claude_query'),


    #############################
    # DOCUMENTS
    path('documents/', TWFDocumentsOverviewView.as_view(), name='documents_overview'),
    path('documents/browse/', TWFDocumentsBrowseView.as_view(), name='documents_browse'),
    path('documents/create/', TWFDocumentCreateView.as_view(), name='documents_create'),
    path('documents/review/', TWFDocumentReviewView.as_view(), name='documents_review'),
    path('documents/name/', TWFDocumentNameView.as_view(), name='name_documents'),
    path('document/<int:pk>/', TWFDocumentDetailView.as_view(), name='view_document'),

    path('documents/batch/openai/', TWFDocumentOpenAIBatchView.as_view(), name='documents_batch_openai'),
    path('documents/batch/gemini/', TWFDocumentGeminiBatchView.as_view(), name='documents_batch_gemini'),
    path('documents/batch/claude/', TWFDocumentClaudeBatchView.as_view(), name='documents_batch_claude'),
    path('documents/page/batch/openai/', TWFDocumentOpenAIPageBatchView.as_view(),
         name='documents_page_batch_openai'),
    path('documents/page/batch/gemini/', TWFDocumentGeminiPageBatchView.as_view(),
         name='documents_page_batch_gemini'),
    path('documents/page/batch/claude/', TWFDocumentClaudePageBatchView.as_view(),
         name='documents_page_batch_claude'),

    #############################
    # TAGS
    path('tags/overview/', TWFTagsOverviewView.as_view(), name='tags_overview'),
    path('tags/extract/', TWFTagsExtractView.as_view(), name='tags_extract'),
    path('tags/all/', TWFProjectTagsView.as_view(template_name='twf/tags/all_tags.html',
                                                 page_title='All Tags'),
         name='tags_all'),
    path('tags/settings/', TWFTagsSettingsView.as_view(), name='tags_settings'),
    path('tags/group/', TWFTagsGroupView.as_view(), name='tags_group'),
    path('tags/dates/', TWFTagsDatesGroupView.as_view(), name='tags_dates'),
    # Tag views
    path('tags/view/parked/', TWFProjectTagsParkedView.as_view(), name='tags_view_parked'),
    path('tags/view/open/', TWFProjectTagsOpenView.as_view(), name='tags_view_open'),
    path('tags/view/resolved/', TWFProjectTagsResolvedView.as_view(), name='tags_view_resolved'),
    path('tags/view/ignored/', TWFProjectTagsIgnoredView.as_view(), name='tags_view_ignored'),
    # Park and unpark tags
    path('tags/park/<int:pk>/', park_tag, name='tags_park'),
    path('tags/unpark/<int:pk>/', unpark_tag, name='tags_unpark'),
    path('tags/ungroup/<int:pk>/', ungroup_tag, name='tags_ungroup'),

    #############################
    # DICTIONARIES
    path('dictionaries/overview', TWFDictionaryOverviewView.as_view(), name='dictionaries_overview'),
    path('dictionaries/', TWFDictionaryDictionariesView.as_view(), name='dictionaries'),
    path('dictionaries/add/', TWFDictionaryAddView.as_view(), name='dictionaries_add'),
    path('dictionaries/add/<int:pk>/', add_dictionary_to_project, name='dictionaries_add_to_project'),
    path('dictionaries/remove/<int:pk>/', remove_dictionary_from_project, name='dictionaries_remove_from_project'),
    path('dictionaries/create/', TWFDictionaryCreateView.as_view(), name='dictionary_create'),
    path('dictionaries/<int:pk>/', TWFDictionaryDictionaryView.as_view(), name='dictionaries_view'),
    path('dictionaries/<int:pk>/edit/', TWFDictionaryDictionaryEditView.as_view(), name='dictionaries_edit'),

    path('dictionaries/entry/<int:pk>/', TWFDictionaryDictionaryEntryView.as_view(), name='dictionaries_entry_view'),
    path('dictionaries/entry/<int:pk>/skip/', skip_entry, name='dictionaries_entry_skip'),
    path('dictionaries/entry/<int:pk>/edit/',
         TWFDictionaryDictionaryEntryEditView.as_view(), name='dictionaries_entry_edit'),
    path('dictionaries/normalization/wizard/', TWFDictionaryNormDataView.as_view(), name='dictionaries_normalization'),
    path('dictionaries/merge/entries/', TWFDictionaryMergeEntriesView.as_view(), name='dictionaries_entry_merging'),
    path('dictionaries/variations/delete/<int:pk>/', delete_variation, name='dictionaries_delete_variation'),

    path('dictionaries/batch/gnd/', TWFDictionaryGNDBatchView.as_view(), name='dictionaries_batch_gnd'),
    path('dictionaries/batch/geonames/', TWFDictionaryGeonamesBatchView.as_view(), name='dictionaries_batch_geonames'),
    path('dictionaries/batch/wikidata/', TWFDictionaryWikidataBatchView.as_view(), name='dictionaries_batch_wikidata'),
    path('dictionaries/batch/openai/', TWFDictionaryOpenaiBatchView.as_view(),
         name='dictionaries_batch_openai'),
    path('dictionaries/batch/claude/', TWFDictionaryClaudeBatchView.as_view(),
         name='dictionaries_batch_claude'),
    path('dictionaries/batch/gemini/', TWFDictionaryGeminiBatchView.as_view(),
         name='dictionaries_batch_gemini'),

    path('dictionaries/request/gnd/', TWFDictionaryGNDRequestView.as_view(), name='dictionaries_request_gnd'),
    path('dictionaries/request/geonames/', TWFDictionaryGeonamesRequestView.as_view(),
         name='dictionaries_request_geonames'),
    path('dictionaries/request/wikidata/', TWFDictionaryWikidataRequestView.as_view(),
         name='dictionaries_request_wikidata'),
    path('dictionaries/request/openai/', TWFDictionaryOpenaiRequestView.as_view(),
         name='dictionaries_request_openai'),
    path('dictionaries/request/claude/', TWFDictionaryClaudeRequestView.as_view(),
         name='dictionaries_request_claude'),
    path('dictionaries/request/gemini/', TWFDictionaryGeminiRequestView.as_view(),
         name='dictionaries_request_gemini'),

    #############################
    # COLLECTIONS
    path('collections/', TWFCollectionOverviewView.as_view(), name='collections'),
    path('collections/list/', TWFCollectionListView.as_view(), name='collections_view'),
    path('collections/create/', TWFCollectionsCreateView.as_view(), name='project_collections_create'),
    path('collections/<int:pk>/', TWFCollectionsDetailView.as_view(), name='collections_view'),
    path('collections/review/', TWFCollectionsReviewView.as_view(), name='collections_review'),
    path('collections/openai/batch/', TWFCollectionsOpenaiBatchView.as_view(), name='collections_openai_batch'),
    path('collections/gemini/batch/', TWFCollectionsGeminiBatchView.as_view(), name='collections_gemini_batch'),
    path('collections/claude/batch/', TWFCollectionsClaudeBatchView.as_view(), name='collections_claude_batch'),
    path('collections/openai/request/', TWFCollectionsOpenaiRequestView.as_view(), name='collections_openai_request'),
    path('collections/gemini/request/', TWFCollectionsGeminiRequestView.as_view(), name='collections_gemini_request'),
    path('collections/claude/request/', TWFCollectionsClaudeRequestView.as_view(), name='collections_claude_request'),

    path('collections/delete/<int:collection_id>/', delete_collection, name='collection_delete'),
    path('collections/edit/<int:pk>/', TWFCollectionsEditView.as_view(), name='collection_edit'),

    path('collections/item/<int:pk>/', TWFCollectionItemView.as_view(), name='collection_item_view'),
    path('collections/item/edit/<int:pk>/', TWFCollectionItemEditView.as_view(), name='collection_item_edit'),
    path('collections/item/copy/<int:pk>/', copy_collection_item, name='collection_item_copy'),
    path('collections/item/delete/<int:pk>/', delete_collection_item, name='collection_item_delete'),
    path('collections/item/download/txt/<int:pk>/', download_collection_item_txt, name='collection_item_download_txt'),
    path('collections/item/download/json/<int:pk>/', download_collection_item_json, name='collection_item_download_json'),
    path('collections/item/split/<int:pk>/<int:index>/', split_collection_item, name='collection_item_split'),
    path('collections/item/delete/anno/<int:pk>/<int:index>/', delete_collection_item_annotation, name='collection_item_delete_annotation'),
    path('collections/item/set_status/<int:pk>/open/', set_col_item_status_open, name='collection_item_status_open'),
    path('collections/item/set_status/<int:pk>/reviewed/', set_col_item_status_reviewed, name='collection_item_status_reviewed'),
    path('collections/item/set_status/<int:pk>/faulty/', set_col_item_status_faulty, name='collection_item_status_faulty'),
    path('collections/<int:pk>/add/document', TWFCollectionsAddDocumentView.as_view(), name='collection_add_document'),

    #############################
    # EXPORT
    path('export/', TWFExportOverviewView.as_view(), name='export_overview'),
    path('export/exports/', TWFExportListView.as_view(), name='export_view_exports'),
    path('export/exports/<int:pk>/delete/', delete_export, name='export_exports_delete'),
    path('export/configuration/', TWFExportConfigurationView.as_view(), name='export_configure'),
    path('export/documents/', TWFExportDocumentsView.as_view(), name='export_documents'),
    path('export/collections/', TWFExportCollectionsView.as_view(), name='export_collections'),
    path('export/project/', TWFExportProjectView.as_view(), name='export_project'),
    path('export/zenodo/', TWFExportZenodoView.as_view(), name='export_to_zenodo'),
    path('export/tags/', TWFExportTagsView.as_view(), name='export_tags'),

    path('export/dictionaries/', TWFExportDictionariesView.as_view(), name='export_dictionaries'),
    path('import/dictionaries/', TWFImportDictionaryView.as_view(), name='import_dictionaries'),

    #############################
    # WORKFLOWS
    path('workflows/documents/review/start/', start_review_document_workflow, name='start_review_document_workflow'),
    path('workflows/collection/review/start/<int:collection_id>/', start_review_collection_workflow,
         name='start_review_collection_workflow'),

    #############################
    # CELERY TASKS
    path('celery/status/<str:task_id>/', task_status_view, name='celery_task_status'),
    path('celery/cancel/<str:task_id>/', task_cancel_view, name='celery_task_cancel'),
    path('celery/remove/<int:pk>/', task_remove_view, name='celery_task_remove'),

    path('celery/transkribus/extract/', start_extraction, name='task_transkribus_extract_export'),
    path('celery/project/copy/', start_copy_project, name='task_project_copy'),

    path('celery/project/query/openai/', start_query_project_openai, name='task_project_query_openai'),
    path('celery/project/query/gemini/', start_query_project_gemini, name='task_project_query_gemini'),
    path('celery/project/query/claude/', start_query_project_claude, name='task_project_query_claude'),


    path('celery/transkribus/tags/extract/', start_tags_creation, name='task_transkribus_extract_tags'),

    path('celery/metadata/sheets/load/', start_sheet_metadata, name='task_metadata_load_sheets'),
    path('celery/metadata/json/load/', start_json_metadata, name='task_metadata_load_json'),

    path('celery/documents/batch/openai/', start_openai_doc_batch, name='task_documents_batch_openai'),
    path('celery/documents/batch/gemini/', start_gemini_doc_batch, name='task_documents_batch_gemini'),
    path('celery/documents/batch/claude/', start_claude_doc_batch, name='task_documents_batch_claude'),
    path('celery/documents/page/batch/openai/', start_openai_page_batch, name='task_documents_page_batch_openai'),
    path('celery/documents/page/batch/gemini/', start_gemini_page_batch, name='task_documents_page_batch_gemini'),
    path('celery/documents/page/batch/claude/', start_claude_page_batch, name='task_documents_page_batch_claude'),

    path('celery/dictionaries/batch/gnd/', start_dict_gnd_batch, name='task_dictionaries_batch_gnd'),
    path('celery/dictionaries/batch/geonames/', start_dict_geonames_batch, name='task_dictionaries_batch_geonames'),
    path('celery/dictionaries/batch/wikidata/', start_dict_wikidata_batch, name='task_dictionaries_batch_wikidata'),
    path('celery/dictionaries/batch/openai/', start_dict_openai_batch, name='task_dictionaries_batch_openai'),
    path('celery/dictionaries/batch/claude/', start_dict_claude_batch, name='task_dictionaries_batch_claude'),
    path('celery/dictionaries/batch/gemini/', start_dict_gemini_batch, name='task_dictionaries_batch_gemini'),

    path('celery/dictionaries/request/gnd/', start_dict_gnd_request, name='task_dictionaries_request_gnd'),
    path('celery/dictionaries/request/geonames/', start_dict_geonames_request, name='task_dictionaries_request_geonames'),
    path('celery/dictionaries/request/wikidata/', start_dict_wikidata_request, name='task_dictionaries_request_wikidata'),
    path('celery/dictionaries/request/openai/', start_dict_openai_request, name='task_dictionaries_request_openai'),
    path('celery/dictionaries/request/claude/', start_dict_claude_request, name='task_dictionaries_request_claude'),
    path('celery/dictionaries/request/gemini/', start_dict_gemini_request, name='task_dictionaries_request_gemini'),

    path('celery/collections/batch/openai/', start_openai_collection_batch, name='task_collection_batch_openai'),
    path('celery/collections/batch/gemini/', start_gemini_collection_batch, name='task_collection_batch_gemini'),
    path('celery/collections/batch/claude/', start_claude_collection_batch, name='task_collection_batch_claude'),
    path('celery/collections/request/openai/', start_openai_collection_request, name='task_collection_request_openai'),
    path('celery/collections/request/gemini/', start_gemini_collection_request, name='task_collection_request_gemini'),
    path('celery/collections/request/claude/', start_claude_collection_request, name='task_collection_request_claude'),

    path('celery/export/documents/', start_export_documents, name='task_export_documents'),
    path('celery/export/collections/', start_export_collections, name='task_export_collections'),
    path('celery/export/project/', start_export_project, name='task_export_project'),
    path('celery/export/zenodo/', start_export_to_zenodo, name='task_export_zenodo'),

    #############################
    # AJAX CALLS
    path('ajax/transkribus/export/request/', ajax_transkribus_request_export,
         name='ajax_transkribus_request_export'),
    path('ajax/transkribus/export/reset/', ajax_transkribus_reset_export,
         name='ajax_transkribus_reset_export'),
    path('ajax/transkribus/export/status/', ajax_transkribus_request_export_status,
         name='ajax_transkribus_request_export__status'),
    path('ajax/transkribus/export/start/download/', ajax_transkribus_download_export,
         name='ajax_transkribus_download_export'),
    path('ajax/transkribus/export/monitor/download/', download_progress_view,
         name='download_progress'),
    path('ajax/markdown-generate/', ajax_markdown_generate,
         name='ajax_markdown_generate'),
    path('ajax/markdown-preview/', ajax_markdown_preview,
         name='ajax_markdown_preview'),
    path('ajax/load/prompt/', load_prompt, name='ajax_load_prompt'),
    path('ajax/save/prompt/', save_prompt, name='ajax_save_prompt'),
    path('ajax/get/prompts/', get_prompts, name='ajax_get_prompts'),
    #############################
    # METADATA
    path('metadata/overview/', TWFMetadataOverviewView.as_view(), name='metadata_overview'),

    path('metadata/load/metadata/', TWFMetadataLoadDataView.as_view(), name='metadata_load_metadata'),
    path('metadata/load/sheets/metadata/', TWFMetadataLoadSheetsDataView.as_view(),
         name='metadata_load_sheets_metadata'),
    path('metadata/extract/tags/', TWFMetadataExtractTagsView.as_view(), name='metadata_extract'),

    path('metadata/review/documents/', TWFMetadataReviewDocumentsView.as_view(), name='metadata_review_documents'),
    path('metadata/review/pages/', TWFMetadataReviewPagesView.as_view(), name='metadata_review_pages'),

    path('validate_page_field/', validate_page_field, name='validate_page_field'),
    path('validate_page_field/', validate_document_field, name='validate_document_field'),
]
