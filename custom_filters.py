# custom_filters.py
from django import template

register = template.Library()

@register.filter
def split_datetime(value):
    return value.split("T")
