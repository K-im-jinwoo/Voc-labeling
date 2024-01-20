from django import template
register = template.Library()

@register.filter
def to_js_boolean(value):
    return str(value).lower()