from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'cnpj', 'cidade', 'estado', 'classificacao_comercial',
        'tipo_fornecimento', 'tensao_nominal_disp'
    )
    search_fields = ('nome', 'cnpj', 'cidade', 'estado')
    list_filter = (
        'estado',
        'classificacao_comercial',
        'tipo_fornecimento'
    )
    ordering = ('nome',)
