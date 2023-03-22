from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.filter
def form_value(value):
    """format the form value depending on if it is a list or a string"""
    if isinstance(value, list):
        return ', '.join(value)
    return value

@register.simple_tag
def event_custom_text(event, id, html=True, default=''):
    from django_bleach.templatetags.bleach_tags import bleach_value
#     return str(event)
    custom_texts = event.config.get('CUSTOM_TEXTS',{})
    custom_text = custom_texts.get(id,{})
    val = bleach_value(custom_text.get('html')) if html else bleach_value(custom_text.get('text'))
    return val or default

@register.filter
def has_custom_text(event, id):
    custom_texts = event.config.get('CUSTOM_TEXTS',{})
    custom_text = custom_texts.get(id,{})
    return custom_text.get('html',False) or custom_text.get('text',False) 

@register.filter
def content_type_id(obj):
    if not obj:
        return False
    return ContentType.objects.get_for_model(obj).pk