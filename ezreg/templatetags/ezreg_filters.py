from django import template

register = template.Library()

@register.filter
def form_value(value):
    """format the form value depending on if it is a list or a string"""
    if isinstance(value, list):
        return ', '.join(value)
    return value

@register.simple_tag
def event_custom_text(event, id, html=True):
    from django_bleach.templatetags.bleach_tags import bleach_value
#     return str(event)
    custom_texts = event.config.get('CUSTOM_TEXTS',{})
    custom_text = custom_texts.get(id,{})
    if html:
        return bleach_value(custom_text.get('html',''))
    return bleach_value(custom_text.get('text',''))