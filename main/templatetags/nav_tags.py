"""Custom template tags for the main app."""
from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, url_name, by_path=False):
    """Returns 'l-active' if the current view is the one specified by url_name, otherwise 'l-inactive'."""
    request = context['request']
    if by_path:
        path = reverse(url_name)
        return "l-active" if request.path == path else "l-inactive"

    return "l-active" if request.resolver_match.url_name == url_name else "l-inactive"


@register.simple_tag
def value_to_color(value):
    """Converts a numerical value from 50 to 100 into a color between red and green."""
    if value < 50:
        return "#FF0000"
    if value > 100:
        return "#00FF00"

    # Calculate green component: Scale value from 50-100 to 0-255
    green = int((value - 50) / 50 * 255)
    # Red component decreases as value increases
    red = 255 - green
    blue = 0  # No blue component needed

    return f"#{red:02x}{green:02x}{blue:02x}"
