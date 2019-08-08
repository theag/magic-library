from django import template

register = template.Library()

@register.filter
def hybrid_png(value):
    if value == "W":
        return "h_white.png"
    elif value == "U":
        return "h_blue.png"
    elif value == "B":
        return "h_black.png"
    elif value == "R":
        return "h_red.png"
    elif value == "G":
        return "h_green.png"