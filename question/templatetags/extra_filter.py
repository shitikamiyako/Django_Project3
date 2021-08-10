"""Template Tag for django html.

This extra filter/tag enables django template engine to add func.
Because I want to add zip func to implement rapidly in for statement."""

from django import template

register = template.Library()


@register.filter(name='zip')
def zip_lists(a, b):
    """To implement zip filter into custom template.

    https://stackoverflow.com/a/14857664"""
    return zip(a, b)
