from django import template

register = template.Library()

@register.filter
def mts_to_hours(minutes_value):
    "converts a duration in minutes to hours& minutes"
    duration_minutes = int(minutes_value)
    if duration_minutes > 0:
        return str(duration_minutes/60) + ' hours, ' + str(duration_minutes%60) + ' minutes'
    else:
        return 0

