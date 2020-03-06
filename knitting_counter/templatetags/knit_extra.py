from django import template
import json

register = template.Library()

@register.filter
def stringify(value):
    return json.dumps(value)