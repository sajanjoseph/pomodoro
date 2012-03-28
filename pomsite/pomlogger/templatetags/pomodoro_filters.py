from django import template
from django.conf import settings

register = template.Library()

@register.filter
def mts_to_hours(minutes_value):
    "converts a duration in minutes to hours& minutes"
    duration_minutes = int(minutes_value)
    if duration_minutes > 0:
        return str(duration_minutes/60) + ' hours, ' + str(duration_minutes%60) + ' minutes'
    else:
        return 0

@register.filter
def adjust_for_pagination(value, page):
    value, page = int(value), int(page)
    adjusted_value = value + ((page - 1) * settings.PAGINATE_BY)
    return adjusted_value