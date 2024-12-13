from django.contrib import admin
from .models import HistoricoConsumoDemanda

@admin.register(HistoricoConsumoDemanda)
class HistoricoConsumoDemandaAdmin(admin.ModelAdmin):
    list_display = (
        'cliente', 'mes',
        'demanda_medida_ponta', 'demanda_medida_fora_ponta', 'demanda_medida_reativo_excedente',
        'consumo_faturado_ponta_tot', 'consumo_faturado_fora_ponta', 'consumo_faturado_reativo_excedente',
        'horario_reservado_consumo', 'horario_reservado_reativo_excedente'
    )
    list_filter = ('cliente', 'mes')
    search_fields = ('cliente__nome',)
    ordering = ('-mes',)
