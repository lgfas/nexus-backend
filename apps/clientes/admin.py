from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'cidade', 'estado', 'fator_potencia')
    search_fields = ('nome', 'cnpj', 'cidade', 'estado')
    list_filter = ('estado', 'classificacao_comercial', 'tipo_fornecimento', 'tipo_tarifa')
    ordering = ('nome',)
