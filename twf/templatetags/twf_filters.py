from django import template

register = template.Library()

@register.inclusion_tag('twf/tables/filter_form.html')
def twf_filter(filter):
    """
    Render a custom filter form for the given filter.
    """
    return {'filter': filter}

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})