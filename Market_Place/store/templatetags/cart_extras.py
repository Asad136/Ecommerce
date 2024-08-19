from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return float(value) * int(arg)

@register.filter
def cart_total(cart):
    total = 0
    for item in cart.values():
        total += float(item['price']) * item['quantity']
    return format(total, '.2f')
