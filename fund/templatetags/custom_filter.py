# templatetags/custom_filter.py

from django import template

register = template.Library()

@register.filter(name='is_minus')
def is_minus(str_value):
    return str_value.startswith('-') and not str_value.startswith('--')
