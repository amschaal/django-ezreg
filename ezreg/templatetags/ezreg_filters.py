from django import template

register = template.Library()

@register.filter
def form_value(value):
    """format the form value depending on if it is a list or a string"""
    if isinstance(value, list):
        return ', '.join(value)
    return value