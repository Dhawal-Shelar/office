from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Multiply filter: multiply a value by an argument
@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except TypeError:
        return value

# Truncate text to N characters
@register.filter
def truncate_chars(value, num):
    try:
        num = int(num)
        if len(value) > num:
            return value[:num] + "..."
        return value
    except Exception:
        return value

# Example tag: render a badge
@register.simple_tag
def badge(text, badge_type="primary"):
    html = f'<span class="badge bg-{badge_type}">{text}</span>'
    return mark_safe(html)

# Example filter: format price
@register.filter
def format_price(value):
    try:
        return f"${float(value):,.2f}"
    except:
        return value
