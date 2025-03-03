from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def render_metadata(metadata):
    """Render metadata with outermost keys as tabs."""

    if metadata is None:
        return mark_safe("<p><em>No metadata available</em></p>")

    if not isinstance(metadata, dict):
        return mark_safe("<p><em>Invalid metadata format</em></p>")

    tab_headers = ""
    tab_contents = ""
    first = True

    for key, value in metadata.items():
        active_class = "active" if first else ""
        show_class = "show active" if first else ""
        tab_headers += f"<li class='nav-item' role='presentation'>"
        tab_headers += f"<button class='nav-link {active_class}' id='{key}-tab' data-bs-toggle='tab' data-bs-target='#{key}' type='button' role='tab' aria-controls='{key}' aria-selected='true'>{key}</button>"
        tab_headers += "</li>"

        tab_contents += f"<div class='tab-pane fade {show_class}' id='{key}' role='tabpanel' aria-labelledby='{key}-tab'>"
        tab_contents += f"{render_metadata_content(value)}"
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


def render_metadata_content(metadata):
    """Helper function to recursively render metadata content."""

    if isinstance(metadata, dict):
        html_render = "<ul>"
        for key, value in metadata.items():
            html_render += f"<li><strong>{key}:</strong> {render_metadata_content(value)}</li>"
        html_render += "</ul>"

    elif isinstance(metadata, list):
        html_render = "<ul>"
        for item in metadata:
            html_render += f"<li>{render_metadata_content(item)}</li>"
        html_render += "</ul>"

    else:
        html_render = f"<p>{metadata}</p>"

    return html_render
