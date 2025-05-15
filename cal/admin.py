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
from .models import Transacao, Tipo

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'valor', 'tipo', 'data', 'user')
    list_filter = ('tipo', 'data')

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ('descricao', 'is_credito')
    list_filter = ('is_credito',)
