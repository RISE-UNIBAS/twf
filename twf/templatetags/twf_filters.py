"""Render custom filters for the table."""
from django import template

register = template.Library()

@register.inclusion_tag('twf/tables/filter_form.html')
def twf_filter(my_twf_filter):
    """
    Render a custom filter form for the given filter.
    """
    return {'filter': my_twf_filter}


@register.filter
def add_class(field, css_class):
    """
    Add a CSS class to the given form field.
    :param field:
    :param css_class:
    :return:
    """
    return field.as_widget(attrs={"class": css_class})


@register.filter
def sum_tags(pages):
    """Count the total number of tags across all pages."""
    return sum(page.tags.count() for page in pages)


@register.filter
def get_tag_types(pages):
    """Get a list of unique tag types across all pages."""
    tag_types = set()
    for page in pages:
        for tag in page.tags.all():
            if tag.variation_type:
                tag_types.add(tag.variation_type)
    return sorted(tag_types)


@register.filter
def truncate_text(text, length=50):
    """Truncate text to the specified length and add ellipsis if needed."""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length] + "..."


@register.filter
def highlight_matches(text, search_term):
    """Highlight search term matches in text."""
    if not text or not search_term:
        return text
    
    # Escape HTML special characters to prevent injection
    from django.utils.html import escape
    text = escape(text)
    search_term = escape(search_term)
    
    # Replace matches with highlighted version
    import re
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    highlighted = pattern.sub(r'<mark>\g<0></mark>', text)
    
    return highlighted
