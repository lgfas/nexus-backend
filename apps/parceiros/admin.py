from django.contrib import admin
from .models import Parceiro

@admin.register(Parceiro)
class ParceiroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'cidade', 'estado', 'tipo', 'telefone', 'email')
    search_fields = ('nome', 'cnpj', 'cidade', 'estado', 'tipo', 'email')
    list_filter = ('estado', 'tipo')
    ordering = ('nome',)

