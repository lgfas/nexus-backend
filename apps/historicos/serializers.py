from rest_framework import serializers
from .models import HistoricoConsumoDemanda

class HistoricoConsumoDemandaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoConsumoDemanda
        fields = [
            'id', 'cliente', 'mes',
            'demanda_medida_ponta', 'demanda_medida_fora_ponta', 'demanda_medida_reativo_excedente',
            'consumo_faturado_ponta_tot', 'consumo_faturado_fora_ponta', 'consumo_faturado_reativo_excedente',
            'horario_reservado_consumo', 'horario_reservado_reativo_excedente'
        ]
