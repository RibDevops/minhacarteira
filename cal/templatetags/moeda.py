from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def moeda(valor):
    if valor is None:
        return "R$ 0,00"
    try:
        valor = Decimal(valor)
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ --"


