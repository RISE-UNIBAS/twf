from django import template

register = template.Library()

@register.simple_tag
def user_has_permission(profile, action, project):
    """Custom filter to check if a profile has a specific permission."""
    if action == '' or action is None:
        return True
    return profile.has_permission(action, project)

@register.simple_tag
def project_permissions(profile, project):
    """Custom filter to check if a profile has a specific permission."""
    return profile.get_project_permissions(project)