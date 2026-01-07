# from django.contrib import admin
# from cal.models import Event

# # Register your models here.
# admin.site.register(Event)

# from django.contrib import admin
# from cal.models import Transacao

# @admin.register(Transacao)
# class TransacaoAdmin(admin.ModelAdmin):
#     list_display = ('titulo', 'valor', 'categoria', 'data', 'fk_user')
#     list_filter = ('categoria', 'data')
#     search_fields = ('titulo',)
from django.contrib import admin
from .models import Transacao, Tipo, FormaPagamento, Cartao

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'valor', 'tipo', 'forma_pagamento', 'cartao', 'data', 'user')
    list_filter = ('tipo', 'forma_pagamento', 'data')

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao')
    list_filter = ('codigo',)

@admin.register(FormaPagamento)
class FormaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descricao', 'exige_cartao')
    list_filter = ('exige_cartao',)

@admin.register(Cartao)
class CartaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'limite', 'dia_fechamento', 'is_credito', 'user')
    list_filter = ('is_credito',)
