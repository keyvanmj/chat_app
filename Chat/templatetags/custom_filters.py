from Chat.utils import calculate_timestamp
from django import template

register = template.Library()


@register.filter
def calculate_time(value):
    timestamp = calculate_timestamp(value)
    return timestamp
