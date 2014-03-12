from django import template
register = template.Library()

@register.filter('fieldtype')
def fieldtype(ob):
    return ob.__class__.__name__
