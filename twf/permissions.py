
def check_permission(user, action, object_id=None):

    # Check if action is valid
    if action not in get_available_actions():
        raise ValueError(f"Action '{action}' is not available.")

    # Check if user is authenticated
    if not user.is_authenticated:
        return False

    # Check if user is superuser
    if user.is_superuser:
        return True

    # Check if user is staff
    if user.is_staff:
        return True # TODO: Implement staff permissions

    # Check if user is project owner
    #
    return True


def get_actions_grouped_by_category():
    actions = get_available_actions()
    grouped_actions = {}

    for action_name, action_details in actions.items():
        group = action_details.get("group", "default")
        if group not in grouped_actions:
            grouped_actions[group] = []
        grouped_actions[group].append({"name": action_name, **action_details})

    return grouped_actions


def get_available_actions():
    return {
        # Project actions
        "create_project": {
            "group": "project",
            "label": "Create project",
        },
        "delete_project": {
            "group": "project",
            "label": "Delete project",
        },
        "close_project": {
            "group": "project",
            "label": "Close project",
        },
        "reopen_project": {
            "group": "project",
            "label": "Reopen project",
        },
        "add_user_to_project": {
            "group": "project",
            "label": "Add user to project",
        },
        "remove_user_from_project": {
            "group": "project",
            "label": "Remove user from project",
        },
        "add_dictionary_to_project": {
            "group": "project",
            "label": "Add dictionary to project",
        },
        "change_credential_settings": {
            "group": "project",
            "label": "Change credentials",
        },
        "change_task_settings": {
            "group": "project",
            "label": "Change task settings",
        },
        "change_export_settings": {
            "group": "project",
            "label": "Change export settings",
        },
        "setup_project_permissions": {
            "group": "project",
            "label": "Setup project permissions",
        },
        # Document actions
        "document_task_batch_action": {
            "group": "document",
            "label": "Document task batch action",
        },
        "document_task_review": {
            "group": "document",
            "label": "Document task review",
        },
        "document_create": {
            "group": "document",
            "label": "Create document",
        },
        # Tag actions
        "tag_task_group": {
            "group": "tag",
            "label": "Group Tags",
        },
        "tag_task_date_normalization": {
            "group": "tag",
            "label": "Date Normalization",
        },
        # Metadata actions
        "metadata_load_json_data": {
            "group": "metadata",
            "label": "Load data",
        },
        "metadata_load_google_sheet_data": {
            "group": "metadata",
            "label": "Load Google Sheet data",
        },
        # Collection actions
        "create_collection": {
            "group": "collection",
            "label": "Create collection",
        },
        "delete_collection": {
            "group": "collection",
            "label": "Delete collection",
        },
        "change_collection_item_status": {
            "group": "collection",
            "label": "Change collection item status",
        },
        "collection_item_edit": {
            "group": "collection",
            "label": "Edit collection item",
        },
        "collection_item_delete": {
            "group": "collection",
            "label": "Delete collection item",
        },
        "collection_item_split": {
            "group": "collection",
            "label": "Split collection item",
        },
        "collection_item_merge": {
            "group": "collection",
            "label": "Merge collection item",
        },
        "collection_item_copy": {
            "group": "collection",
            "label": "Copy collection item",
        },
        "collection_item_delete_annotation": {
            "group": "collection",
            "label": "Delete collection item annotation",
        },
        # Task actions
        "cancel_task": {
            "group": "task",
            "label": "Cancel task",
        },
        "remove_task": {
            "group": "task",
            "label": "Remove task",
        },
        # Prompt actions
        "delete_prompt": {
            "group": "prompt",
            "label": "Delete prompt",
        },
    }
