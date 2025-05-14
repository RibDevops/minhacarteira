# from django.contrib import admin
# from cal.models import Event

# # Register your models here.
# admin.site.register(Event)

from django.contrib import admin
from cal.models import Transacao

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'valor', 'categoria', 'data', 'fk_user')
    list_filter = ('categoria', 'data')
    search_fields = ('titulo',)
