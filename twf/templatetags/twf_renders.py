from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_metadata(obj_with_metadata):
    """Render metadata with outermost keys as tabs."""

    if obj_with_metadata.metadata is None:
        return mark_safe("<p><em>No metadata available</em></p>")

    if not isinstance(obj_with_metadata.metadata, dict):
        return mark_safe("<p><em>Invalid metadata format</em></p>")

    tab_headers = ""
    tab_contents = ""
    first = True
    obj_id = obj_with_metadata.id
    obj_type = obj_with_metadata.__class__.__name__.lower()

    for key, value in obj_with_metadata.metadata.items():
        active_class = "active" if first else ""
        show_class = "show active" if first else ""
        tab_headers += f"<li class='nav-item' role='presentation'>"
        tab_headers += f"<button class='nav-link {active_class}' id='{key}-tab' data-bs-toggle='tab' data-bs-target='#{key}' type='button' role='tab' aria-controls='{key}' aria-selected='true'>{key}</button>"
        tab_headers += f"""<button class='btn btn-sm btn-circle btn-delete show-danger-modal ms-1'
                                  title='Delete entire "{key}" section'
                                  data-message='Are you sure you want to delete the entire metadata section "{key}"?'
                                  data-start-url='/metadata/delete/{obj_type}/{obj_id}/{key}/'
                                  data-delete-base-key='{key}'>
                              <i class='fas fa-trash'></i>
                          </button>"""
        tab_headers += "</li>"

        tab_contents += f"<div class='tab-pane fade {show_class}' id='{key}' role='tabpanel' aria-labelledby='{key}-tab'>"
        tab_contents += f"{render_metadata_content(key, obj_type, obj_id, value)}"
        tab_contents += "</div>"

        first = False

    html_render = f"""
    <ul class='nav nav-tabs' id='metadataTabs' role='tablist'>
        {tab_headers}
    </ul>
    <div class='tab-content' id='metadataTabsContent'>
        {tab_contents}
    </div>
    """

    return mark_safe(html_render)


def render_metadata_content(base_key, obj_type, obj_id, metadata, parent_key=None):
    """Helper function to recursively render metadata content with edit/delete options."""

    if isinstance(metadata, dict):
        html_render = "<ul class='metadata-list'>"
        for key, value in metadata.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            html_render += f"""
            <li id='metadata-{full_key}' class='metadata-item'>
                <button class='btn btn-sm btn-circle btn-edit' onclick='editMetadata("{base_key}", "{obj_type}", "{obj_id}", "{full_key}")' title='Edit'>
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-circle btn-delete show-danger-modal"
                        data-message="Are you sure you want to delete the key '{full_key}'?"
                        data-start-url="/metadata/delete/{obj_type}/{obj_id}/{base_key}/"
                        data-delete-md-key="{full_key}">
                    <i class="fas fa-trash"></i>
                </button>
                <strong>{key}:</strong> 
                <span id="metadata-value-{full_key}">{render_metadata_content(base_key, obj_type, obj_id, value, full_key)}</span>
            </li>
            """
        html_render += "</ul>"

    elif isinstance(metadata, list):
        html_render = "<ul class='metadata-list'>"
        for index, item in enumerate(metadata):
            full_key = f"{parent_key}[{index}]" if parent_key else str(index)
            html_render += f"""
            <li id='metadata-{full_key}' class='metadata-item'>
                {render_metadata_content(base_key, obj_type, obj_id, item, full_key)}
            </li>
            """
        html_render += "</ul>"

    else:
        html_render = f"""
        <span id='metadata-{parent_key}'>{metadata}</span>
        """

    return html_render


