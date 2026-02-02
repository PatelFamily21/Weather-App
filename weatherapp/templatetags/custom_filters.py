from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """
    Multiplies the value by the argument.
    
    Usage: {{ value|multiply:2 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
