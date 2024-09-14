import re

from twf.models import Document, Page, Project


def create_data(db_object, return_warnings=False):
    if isinstance(db_object, Project):
        return create_project_data(db_object, return_warnings)
    elif isinstance(db_object, Document):
        return create_document_data(db_object, return_warnings)
    elif isinstance(db_object, Page):
        return create_page_data(db_object, return_warnings)
    else:
        raise ValueError(f"Invalid object type: {db_object}")


def create_project_data(project, return_warnings=False):
    project_Export = []
    all_warnings = []
    for document in project.documents.all():
        if return_warnings:
            document_data, warnings = create_document_data(document, True)
            all_warnings.extend(warnings)
        else:
            document_data = create_document_data(document)
        project_Export.append(document_data)

    if return_warnings:
        return project_Export, all_warnings

    return project_Export


def create_document_data(document, return_warnings=False):
    data = {**document.metadata}
    all_warnings = []
    config = document.project.document_export_configuration
    if return_warnings:
        doc_export, warnings = create_data_from_config(data, config, document, True)
        all_warnings.extend(warnings)
    else:
        doc_export = create_data_from_config(data, config, document)

    doc_export['pages'] = []
    for page in document.pages.all():
        if return_warnings:
            page_data, warnings = create_page_data(page, True)
            all_warnings.extend(warnings)
        else:
            page_data = create_page_data(page)
        doc_export['pages'].append(page_data)

    if return_warnings:
        return doc_export, all_warnings
    return doc_export


def create_page_data(page, return_warnings=False):
    data = {**page.parsed_data, **page.metadata}
    config = page.document.project.page_export_configuration
    return create_data_from_config(data, config, page, return_warnings)


def create_data_from_config(metadata, config, db_object=None, return_warnings=False):
    transformed = {}
    warnings = []

    for key, mapping in config.items():
        if "value" not in mapping:
            warnings.append(f"Missing 'value' key in mapping for '{key}'")
            value_expression = ""
        else:
            value_expression = mapping['value']

        if "empty_value" not in mapping:
            empty_value = ""
        else:
            empty_value = mapping['empty_value']

        # Handle nested structures (e.g., "project.name.short")
        if '.' in key:
            keys = key.split('.')
            current_level = transformed

            # Traverse the keys to create the nested dictionary
            for i, sub_key in enumerate(keys):
                if i == len(keys) - 1:
                    # Final key: assign the value
                    if value_expression.startswith('{__') and value_expression.endswith('__}'):
                        # Handle access to DB fields like "{__tk_page_number__}"
                        db_field = value_expression[3:-3]
                        if db_object:
                            try:
                                attr = getattr(db_object, db_field)
                                if callable(attr):
                                    # If it's a method, call it
                                    current_level[sub_key] = attr()
                                else:
                                    # Otherwise, it's a field, so just assign its value
                                    current_level[sub_key] = attr
                            except AttributeError:
                                warnings.append(f"Key '{key}' ({db_field}) missing in DB object")
                                current_level[sub_key] = empty_value
                        else:
                            warnings.append(f"Key '{key}' requires a DB object")
                            transformed[key] = empty_value
                    elif value_expression.startswith('{') and value_expression.endswith('}'):
                        # Handle simple dynamic references like "{tags1}"
                        metadata_key = value_expression[1:-1]
                        current_level[sub_key] = metadata.get(metadata_key, empty_value)
                    elif '{' in value_expression and '}' in value_expression:
                        # Handle formatted strings like "p. {page}"
                        try:
                            current_level[sub_key] = value_expression.format(**metadata)
                        except KeyError:
                            warnings.append(f"Key '{key}' ({sub_key}) missing in metadata")
                            current_level[sub_key] = empty_value
                    else:
                        # Handle static values
                        current_level[sub_key] = value_expression
                else:
                    # Traverse deeper, create nested dictionary if needed
                    if sub_key not in current_level:
                        current_level[sub_key] = {}
                    current_level = current_level[sub_key]
        else:
            # No nested structure
            if value_expression.startswith('{__') and value_expression.endswith('__}'):
                # Handle access to DB fields like "{__tk_page_number__}"
                db_field = value_expression[3:-3]
                if db_object:
                    try:
                        attr = getattr(db_object, db_field)
                        if callable(attr):
                            # If it's a method, call it
                            transformed[key] = attr()
                        else:
                            # Otherwise, it's a field, so just assign its value
                            transformed[key] = attr
                    except AttributeError:
                        warnings.append(f"Key '{key}' ({db_field}) missing in DB object")
                        transformed[key] = empty_value
                else:
                    warnings.append(f"Key '{key}' requires a DB object")
                    transformed[key] = empty_value
            elif value_expression.startswith('{') and value_expression.endswith('}'):
                # Handle simple dynamic references like "{tags1}"
                metadata_key = value_expression[1:-1]
                transformed[key] = metadata.get(metadata_key, empty_value)
            elif '{__' in value_expression and '__}' in value_expression:
                # Handle access to DB fields in formatted strings like "p. {__tk_page_number__}"
                db_field = re.findall(r'{__(.*?)__}', value_expression)[0]
                if db_object:
                    transformed[key] = value_expression.format(**{"__"+db_field+"__": getattr(db_object, db_field)})
                else:
                    warnings.append(f"Key '{key}' requires a DB object")
                    transformed[key] = empty_value
            elif '{' in value_expression and '}' in value_expression:
                # Handle formatted strings like "p. {page}"
                try:
                    transformed[key] = value_expression.format(**metadata)
                except KeyError:
                    warnings.append(f"Key '{key}' missing in metadata")
                    transformed[key] = empty_value
            else:
                # Handle static values
                transformed[key] = value_expression

    if return_warnings:
        return transformed, warnings
    return transformed


def flatten_dict_keys(d, parent_key='', sep='.'):
    """
    Recursively flatten a dictionary and list to get keys in 'dot notation'.
    Only the first element of a list will be processed.

    :param d: The dictionary (or list) to flatten.
    :param parent_key: The base key (used in recursion).
    :param sep: The separator between keys (default is dot).
    :return: A list of keys in 'dot notation'.
    """
    keys = []
    if isinstance(d, dict):
        # Iterate through dictionary items
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                # Recurse into dictionary
                keys.extend(flatten_dict_keys(v, new_key, sep=sep))
            elif isinstance(v, list) and v:
                # Only handle the first item in the list
                list_key = f"{new_key}{sep}0"
                keys.extend(flatten_dict_keys(v[0], list_key, sep=sep))
            else:
                # Add simple key
                keys.append(new_key)
    elif isinstance(d, list) and d:
        # Only handle the first item in the list
        list_key = f"{parent_key}{sep}0"
        keys.extend(flatten_dict_keys(d[0], list_key, sep=sep))
    else:
        # Add key for simple values
        keys.append(parent_key)
    return keys

