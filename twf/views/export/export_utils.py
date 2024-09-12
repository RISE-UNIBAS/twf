def transform_page_metadata(metadata, config):
    transformed = {}

    for key, mapping in config['pages'].items():
        if '.' in key:
            # Nested structure, handle as dictionary
            outer_key, inner_key = key.split('.')
            if outer_key not in transformed:
                transformed[outer_key] = {}

            # Apply value mapping
            value_key = mapping['value']
            # Use .get to handle missing keys
            transformed[outer_key][inner_key] = metadata.get(value_key, [])
        else:
            # Direct mapping
            value_template = mapping['value']
            if '{' in value_template and '}' in value_template:
                # Handle template formatting (e.g., "p. {page}")
                try:
                    formatted_value = value_template.format(**metadata)
                except KeyError:
                    formatted_value = value_template.format(page="")  # Provide default value if key is missing
                transformed[key] = formatted_value
            else:
                # Simple value assignment with default if key is missing
                transformed[key] = metadata.get(value_template, "")

    return transformed
