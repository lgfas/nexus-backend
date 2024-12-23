from rest_framework import serializers

from apps.clientes.models import Cliente
from .models import ContaEnergia
from .models import ItemFatura


class ItemFaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemFatura
        fields = '__all__'

    def validate(self, data):
        # Substitui valores nulos por zero
        for field in ['quantidade', 'preco_unitario', 'tarifa', 'pis_cofins', 'icms', 'valor']:
            if data.get(field) is None:
                data[field] = 0.0
        return data


class ContaEnergiaSerializer(serializers.ModelSerializer):
    itens_fatura = ItemFaturaSerializer(many=True, read_only=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(),
        source='cliente',
        write_only=True
    )

    class Meta:
        model = ContaEnergia
        fields = [
            'id',
            'cliente_id',
            'mes',
            'vencimento',
            'total_pagar',
            'leitura_anterior',
            'leitura_atual',
            'numero_dias',
            'proxima_leitura',
            'demanda_contratada',
            'itens_fatura',
        ]
