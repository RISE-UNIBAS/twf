from django.utils.safestring import mark_safe


def check_permission(user, action, project, object_id=None):

    # Check if action is valid
    if action not in get_available_actions():
        raise ValueError(f"Action '{action}' is not available.")

    # Check if user is authenticated
    if not user.is_authenticated:
        return False

    if not user.is_active:
        return False

    # Check if user is superuser
    if user.is_superuser:
        return True

    # Check if user is staff
    if user.is_staff:
        return True # TODO: Implement staff permissions

    # Check if user is project owner
    #
    return user.profile.has_permission(action, project)

def can_create_project(user):
    """Check if a user can create a project."""
    if user.is_superuser or user.is_staff:
        return True

def get_actions_grouped_by_category(project, profile=None):
    """Return a dictionary of actions grouped by category.
    If a profile is provided, only return actions that the profile has permission for."""
    actions = get_available_actions(project, profile=profile)
    grouped_actions = {}

    for action_name, action_details in actions.items():
        group = action_details.get("group", "default")
        if group not in grouped_actions:
            grouped_actions[group] = []
        grouped_actions[group].append({"name": action_name, **action_details})

    return grouped_actions


def get_available_actions(project=None, profile=None, for_group=None):
    """Return a dictionary of available actions with their details.
    If a profile is provided, only return actions that the profile has permission for."""

    available_actions = {
        # Project actions
        "delete_project": {
            "group": "project",
            "label": "Delete project",
            "description": mark_safe('Delete a project. <span class="text-danger">This cannot be undone and is '
                                     'permanent.</span>'),
            "default_for": []
        },
        "close_project": {
            "group": "project",
            "label": "Close project",
            "description": mark_safe('Close a project. <span class="text-danger">This will prevent any further '
                                     'actions on the project.</span>'),
            "default_for": ["manager"]
        },
        "reopen_project": {
            "group": "project",
            "label": "Reopen project",
            "description": mark_safe('Reopen a project. <span class="text-danger">Not implemented yet.</span>'),
            "default_for": ["manager"]
        },
        "copy_project": {
            "group": "project",
            "label": "Copy project",
            "description": "Copy a project.",
            "default_for": ["manager"]
        },
        "change_project_settings": {
            "group": "project",
            "label": "Change project settings",
            "description": "Change the project settings.",
            "default_for": ["manager"]
        },
        "change_credential_settings": {
            "group": "project",
            "label": "Change credentials",
            "description": "Change the credential settings for the project.",
            "default_for": ["manager"]
        },
        "change_task_settings": {
            "group": "project",
            "label": "Change task settings",
            "description": "Change the task settings for the project.",
            "default_for": ["manager"]
        },
        "change_export_settings": {
            "group": "project",
            "label": "Change export settings",
            "description": "Change the export settings for the project.",
            "default_for": ["manager"]
        },
        "setup_project_permissions": {
            "group": "project",
            "label": "Setup project permissions",
            "description": "Setup the project permissions.",
            "default_for": []
        },
        "request_transkribus_export": {
            "group": "project",
            "label": "Request Transkribus export",
            "description": "Request a Transkribus export.",
            "default_for": ["manager"]
        },
        "test_transkribus_export": {
            "group": "project",
            "label": "Test Transkribus export (NIY)",
            "description": "Test a Transkribus export.",
            "default_for": ["manager"]
        },
        "extract_transkribus_export": {
            "group": "project",
            "label": "Extract Transkribus export",
            "description": "Extract a Transkribus export.",
            "default_for": ["manager"]
        },
        "delete_all_documents": {
            "group": "project",
            "label": "Delete all documents",
            "description": "Delete all documents in the project.",
            "default_for": ["manager"]
        },
        "delete_all_tags": {
            "group": "project",
            "label": "Delete all tags",
            "description": "Delete all tags in the project.",
            "default_for": ["manager"]
        },
        "delete_all_collections": {
            "group": "project",
            "label": "Delete all collections",
            "description": "Delete all collections in the project.",
            "default_for": ["manager"]
        },
        ###############################
        # Document actions
        "document_batch_workflow_openai": {
            "group": "document",
            "label": "OpenAI Batch Workflow",
            "description": "User is allowed to start an OpenAI batch workflow.",
            "default_for": ["manager"]
        },
        "document_batch_workflow_gemini": {
            "group": "document",
            "label": "Gemini Batch Workflow",
            "description": "User is allowed to start a Gemini batch workflow.",
            "default_for": ["manager"]
        },
        "document_batch_workflow_claude": {
            "group": "document",
            "label": "Claude Batch Workflow",
            "description": "User is allowed to start a Claude batch workflow.",
            "default_for": ["manager"]
        },
        "document_task_review": {
            "group": "document",
            "label": "Document task review",
            "description": "User is allowed to review documents.",
            "default_for": ["manager", "user"]
        },
        "document_create": {
            "group": "document",
            "label": "Create document",
            "description": "User is allowed to manually create documents.",
            "default_for": ["manager"]
        },
        ###############################
        # Tag actions
        "tags_extract": {
            "group": "tag",
            "label": "Extract tags",
            "description": "User is allowed to extract tags.",
            "default_for": ["manager"]
        },
        "tag_task_group": {
            "group": "tag",
            "label": "Group Tags",
            "description": "User is allowed to group tags.",
            "default_for": ["manager", "user"]
        },
        "tag_task_date_normalization": {
            "group": "tag",
            "label": "Date Normalization",
            "description": "User is allowed to normalize dates.",
            "default_for": ["manager", "user"]
        },
        ###############################
        # Metadata actions
        "metadata_load_json_data": {
            "group": "metadata",
            "label": "Load data",
            "description": "User is allowed to load data.",
            "default_for": ["manager"]
        },
        "metadata_load_google_sheet_data": {
            "group": "metadata",
            "label": "Load Google Sheet data",
            "description": "User is allowed to load Google Sheet data.",
            "default_for": ["manager"]
        },
        "metadata_extract_values": {
            "group": "metadata",
            "label": "Extract controlled values",
            "description": "User is allowed to extract controlled values.",
            "default_for": ["manager"]
        },
        "metadata_review_documents": {
            "group": "metadata",
            "label": "Review documents",
            "description": "User is allowed to review documents.",
            "default_for": ["manager"]
        },
        "metadata_review_pages": {
            "group": "metadata",
            "label": "Review pages",
            "description": "User is allowed to review pages.",
            "default_for": ["manager"]
        },
        ###############################
        # Dictionary actions
        "dictionary_add": {
            "group": "dictionary",
            "label": "Add dictionary",
            "description": "User is allowed to add an existing dictionary to a project.",
            "default_for": ["manager"]
        },
        "dictionary_create": {
            "group": "dictionary",
            "label": "Create dictionary",
            "description": "User is allowed to create a dictionary.",
            "default_for": ["manager"]
        },
        "dictionary_batch_workflow_gnd": {
            "group": "dictionary",
            "label": "GND Batch Workflow",
            "description": "User is allowed to start a GND batch workflow.",
            "default_for": ["manager"]
        },
        "dictionary_batch_workflow_wikidata": {
            "group": "dictionary",
            "label": "Wikidata Batch Workflow",
            "description": "User is allowed to start a Wikidata batch workflow.",
            "default_for": ["manager"]
        },
        "dictionary_batch_workflow_openai": {
            "group": "dictionary",
            "label": "OpenAI Batch Workflow",
            "description": "User is allowed to start an OpenAI batch workflow.",
            "default_for": ["manager"]
        },
        "dictionary_batch_workflow_geonames": {
            "group": "dictionary",
            "label": "Geonames Batch Workflow",
            "description": "User is allowed to start a Geonames batch workflow.",
            "default_for": ["manager"]
        },
        "dictionary_manual_workflow_gnd": {
            "group": "dictionary",
            "label": "GND Manual Workflow",
            "description": "User is allowed to start a GND manual workflow.",
            "default_for": ["manager", "user"]
        },
        "dictionary_manual_workflow_wikidata": {
            "group": "dictionary",
            "label": "Wikidata Manual Workflow",
            "description": "User is allowed to start a Wikidata manual workflow.",
            "default_for": ["manager", "user"]
        },
        "dictionary_manual_workflow_openai": {
            "group": "dictionary",
            "label": "OpenAI Manual Workflow",
            "description": "User is allowed to start an OpenAI manual workflow.",
            "default_for": ["manager", "user"]
        },
        "dictionary_manual_workflow_geonames": {
            "group": "dictionary",
            "label": "Geonames Manual Workflow",
            "description": "User is allowed to start a Geonames manual workflow.",
            "default_for": ["manager", "user"]
        },
        "dictionary_merge_entries": {
            "group": "dictionary",
            "label": "Merge entries",
            "description": "User is allowed to merge dictionary entries.",
            "default_for": ["manager"]
        },
        ###############################
        # Collection actions
        "create_collection": {
            "group": "collection",
            "label": "Create collection",
            "description": "User is allowed to create a collection.",
            "default_for": ["manager"]
        },
        "delete_collection": {
            "group": "collection",
            "label": "Delete collection",
            "description": "User is allowed to delete a collection.",
            "default_for": ["manager"]
        },
        "change_collection_item_status": {
            "group": "collection",
            "label": "Change collection item status",
            "description": "User is allowed to change the status of a collection item.",
            "default_for": ["manager", "user"]
        },
        "collection_item_edit": {
            "group": "collection",
            "label": "Edit collection item",
            "description": "User is allowed to edit a collection item.",
            "default_for": ["manager", "user"]
        },
        "collection_item_delete": {
            "group": "collection",
            "label": "Delete collection item",
            "description": "User is allowed to delete a collection item.",
            "default_for": ["manager", "user"]
        },
        "collection_item_split": {
            "group": "collection",
            "label": "Split collection item",
            "description": "User is allowed to split a collection item.",
            "default_for": ["manager", "user"]
        },
        "collection_item_merge": {
            "group": "collection",
            "label": "Merge collection item",
            "description": "User is allowed to merge a collection item.",
            "default_for": ["manager", "user"]
        },
        "collection_item_copy": {
            "group": "collection",
            "label": "Copy collection item",
            "description": "User is allowed to copy a collection item.",
            "default_for": ["manager", "user"]
        },
        "collection_item_delete_annotation": {
            "group": "collection",
            "label": "Delete collection item annotation",
            "description": "User is allowed to delete a collection item annotation.",
            "default_for": ["manager", "user"]
        },
        "collection_openai_batch": {
            "group": "collection",
            "label": "OpenAI Batch",
            "description": "User is allowed to start an OpenAI batch.",
            "default_for": ["manager"]
        },
        "collection_openai_workflow":   {
            "group": "collection",
            "label": "OpenAI Workflow",
            "description": "User is allowed to start an OpenAI workflow.",
            "default_for": ["manager", "user"]
        },
        "collection_item_naming_workflow": {
            "group": "collection",
            "label": "OpenAI Workflow",
            "description": "User is allowed to start an OpenAI workflow.",
            "default_for": ["manager", "user"]
        },
        ###############################
        # Import Export actions
        "import_dictionaries": {
            "group": "import_export",
            "label": "Import dictionary",
            "description": "User is allowed to import a dictionary.",
            "default_for": ["manager"]
        },
        "export_configure": {
            "group": "import_export",
            "label": "Export configurations",
            "description": "User is allowed change export configurations.",
            "default_for": ["manager"]
        },
        "export_documents": {
            "group": "import_export",
            "label": "Export documents",
            "description": "User is allowed to export documents.",
            "default_for": ["manager"]
        },
        "export_collections": {
            "group": "import_export",
            "label": "Export collections",
            "description": "User is allowed to export collections.",
            "default_for": ["manager"]
        },
        "export_dictionaries": {
            "group": "import_export",
            "label": "Export dictionaries",
            "description": "User is allowed to export dictionaries.",
            "default_for": ["manager"]
        },
        "export_tags": {
            "group": "import_export",
            "label": "Export tags",
            "description": "User is allowed to export tags.",
            "default_for": ["manager"]
        },
        "export_project": {
            "group": "import_export",
            "label": "Export project",
            "description": "User is allowed to export a project.",
            "default_for": ["manager"]
        },
        ###############################
        # Task actions
        "cancel_task": {
            "group": "task",
            "label": "Cancel task",
            "description": "User is allowed to cancel a task.",
            "default_for": ["manager"]
        },
        "remove_task": {
            "group": "task",
            "label": "Remove task",
            "description": "User is allowed to remove a task.",
            "default_for": ["manager"]
        },
        ###############################
        # Prompt actions
        "delete_prompt": {
            "group": "prompt",
            "label": "Delete prompt",
            "description": "User is allowed to delete a prompt.",
            "default_for": ["manager"]
        },
    }

    if profile:
        filtered_actions = {}
        for action_name, action_details in available_actions.items():
            if profile.has_permission(action_name, project):
                filtered_actions[action_name] = action_details
        return filtered_actions

    if for_group:
        filtered_actions = {}
        for action_name, action_details in available_actions.items():
            if action_details["default_for"] and for_group in action_details["default_for"]:
                filtered_actions[action_name] = action_details
        return filtered_actions

    return available_actions
