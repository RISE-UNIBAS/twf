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
