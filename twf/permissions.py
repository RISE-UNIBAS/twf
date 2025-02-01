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


def get_available_actions(project=None, profile=None):
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
            "default_for": []
        },
        "reopen_project": {
            "group": "project",
            "label": "Reopen project",
            "description": mark_safe('Reopen a project. <span class="text-danger">Not implemented yet.</span>'),
            "default_for": []
        },
        "change_project_settings": {
            "group": "project",
            "label": "Change project settings",
            "description": "Change the project settings.",
            "default_for": []
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
        ###############################
        # Document actions
        "document_task_batch_action": {
            "group": "document",
            "label": "Document task batch action",
            "description": "User is allowed to perform a batch task. These are ChatGPT, Gemini and Claude document batches.",
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
        # Tag actions
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

    return available_actions
