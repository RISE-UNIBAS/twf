"""Urls for the twf app."""
from django.views.generic import TemplateView
from django.urls import path
from django.contrib.auth import views as auth_views

from .views.views_ajax_metadata import start_metadata_extraction, stream_metadata_extraction_progress
from .views.views_ajax_tags import start_tag_extraction, stream_tag_extraction_progress, \
    stream_tag_extraction_progress_detail
from .views.views_command import park_tag, unpark_tag
from .views.views_dict_auth import DictionaryAuthViewWikidata, DictionaryAuthViewGeonames, DictionaryAuthViewGND, \
    DictionaryAuthViewManual
from .views.views_dictionaries import DictionaryOverView, DictionaryView, DictionaryEntryView, delete_entry, \
    delete_variation, DictionaryExportView
from .views.views_project_collections import ProjectCollectionsView
from .views.views_project_documents import ProjectDocumentView, DocumentView, delete_document
from .views.views_project_export import ProjectExportView
from .views.views_project_overview import ProjectOverView
from .views.views_project_setup import ProjectSetupView
from .views.views_project_tags import ProjectGroupTagsView, ProjectGroupWizardView, ProjectParkedTagsView, \
    ProjectSpecialTagsView
from .views_general import assign_tag, assign_tag_to_new_entry, assign_tag_by_variation
from .forms import LoginForm
from .views.views_ajax_download import ajax_transkribus_download_export, download_progress_view
from .views.views_ajax_export import ajax_transkribus_request_export_status, ajax_transkribus_request_export
from .views.views_ajax_extract import start_extraction, stream_extraction_progress, stream_extraction_progress_detail

urlpatterns = [
    # Project
    path('project/<int:pk>/', ProjectOverView.as_view(), name='project_overview'),
    path('project/<int:pk>/set_up/', ProjectSetupView.as_view(), name='project'),
    path('project/<int:pk>/documents/', ProjectDocumentView.as_view(), name='documents'),

    path('project/<int:pk>/collections/', ProjectCollectionsView.as_view(), name='project_collections'),
    path('project/<int:pk>/export/', ProjectExportView.as_view(), name='project_export'),

    # Tags
    path('project/<int:pk>/tags/group/', ProjectGroupTagsView.as_view(), name='project_group_tags'),
    path('project/<int:pk>/tags/group/wizard/', ProjectGroupWizardView.as_view(), name='project_group_wizard'),
    path('project/<int:pk>/tags/parked/', ProjectParkedTagsView.as_view(), name='project_parked_tags'),
    path('project/<int:pk>/tags/special/', ProjectSpecialTagsView.as_view(), name='project_special_tags'),
    path('project/<int:pk>/tags/group/<str:tag_type>/', ProjectGroupTagsView.as_view(), name='project_group_tags_type'),


    path('tags/park/<int:pk>/', park_tag, name='park_tag'),
    path('tags/unpark/<int:pk>/', unpark_tag, name='unpark_tag'),
    path('tags/assign/<int:pk>/to/<int:entry_id>/', assign_tag, name='assign_tag_to_entry'),
    path('tags/assign/<int:pk>/to/new/entry', assign_tag_to_new_entry, name='assign_tag_to_new_entry'),
    path('tags/assign/<int:pk>/by/variation/<int:variation_id>/', assign_tag_by_variation,
         name='assign_tag_by_variation'),

    # Documents
    path('project/<int:pk>/document/<int:doc_pk>/view/', DocumentView.as_view(), name='view_document'),
    path('project/<int:pk>/document/<int:doc_pk>/delete/', delete_document, name='delete_document'),

    # Dictionaries
    path('dictionaries/', DictionaryOverView.as_view(), name='dictionaries'),
    path('dictionary/<int:pk>/', DictionaryView.as_view(), name='dictionary'),
    path('dictionary/export/<int:pk>/', DictionaryExportView.as_view(), name='dictionary_export'),

    path('dictionaries/entry/delete/<int:pk>/', delete_entry, name='delete_entry'),
    path('dictionaries/entry/view/<int:pk>/', DictionaryEntryView.as_view(), name='view_entry'),

    path('dictionaries/variation/delete/<int:pk>/', delete_variation, name='delete_variation'),


    path('dictionaries/auth/manual/', DictionaryAuthViewManual.as_view(), name='auth_manual'),
    path('dictionaries/auth/wikidata/', DictionaryAuthViewWikidata.as_view(), name='auth_wikidata'),
    path('dictionaries/auth/geonames/', DictionaryAuthViewGeonames.as_view(), name='auth_geonames'),
    path('dictionaries/auth/gnd/', DictionaryAuthViewGND.as_view(), name='auth_gnd'),

    path('dictionaries/auth/select/<int:pk>/', DictionaryAuthViewWikidata.as_view(), name='auth_select'),


    #############################
    # AJAX CALLS
    path('ajax/transkribus/export/request/', ajax_transkribus_request_export, name='ajax_transkribus_request_export'),
    path('ajax/transkribus/export/status/', ajax_transkribus_request_export_status,
         name='ajax_transkribus_request_export__status'),
    path('ajax/transkribus/export/start/download/<int:project_id>/', ajax_transkribus_download_export,
         name='ajax_transkribus_download_export'),
    path('ajax/transkribus/export/monitor/download/', download_progress_view, name='download_progress'),
    path('ajax/transkribus/extract/<int:project_id>/', start_extraction, name='extract_and_process_zip'),
    path('ajax/transkribus/extract/tags/<int:project_id>/', start_tag_extraction, name='start_tag_extraction'),
    path('ajax/transkribus/extract/metadata/<int:project_id>/', start_metadata_extraction,
         name='start_metadata_extraction'),
    path('ajax/transkribus/extract/monitor/<int:project_id>/', stream_extraction_progress,
         name='stream_extraction_progress'),
    path('ajax/transkribus/extract/monitor/<int:project_id>/details/', stream_extraction_progress_detail,
         name='stream_extraction_progress_detail'),
    path('ajax/transkribus/extract/tags/monitor/<int:project_id>/', stream_tag_extraction_progress,
         name='stream_tag_extraction_progress'),
    path('ajax/transkribus/extract/tags/monitor/<int:project_id>/details/', stream_tag_extraction_progress_detail,
         name='stream_tag_extraction_progress_detail'),
    path('ajax/transkribus/extract/metadata/monitor/<int:project_id>/', stream_metadata_extraction_progress,
         name='stream_metadata_extraction_progress'),

    #############################
    # FRAMEWORK
    path('', TemplateView.as_view(template_name='twf/home.html'), name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='twf/login.html',
                                                authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='twf:home'), name='logout'),
]
