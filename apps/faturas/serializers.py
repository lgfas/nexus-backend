from rest_framework import serializers

from apps.clientes.models import Cliente
from .models import ContaEnergia, Tributo
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
    class Meta:
        model = ContaEnergia
        fields = [
            'id', 'cliente', 'mes', 'vencimento', 'total_pagar',
            'leitura_anterior', 'leitura_atual', 'proxima_leitura',
            'numero_dias', 'subgrupo', 'tipo_tarifa_bt', 'tipo_tarifa_at',
            'demanda_contratada_unica', 'demanda_contratada_ponta', 'demanda_contratada_fora_ponta',
            'fator_potencia',
        ]

    def validate(self, data):
        subgrupo = data.get('subgrupo')
        tipo_tarifa_bt = data.get('tipo_tarifa_bt')
        tipo_tarifa_at = data.get('tipo_tarifa_at')

        # Validações de Subgrupo BT
        if subgrupo == 'BT':
            if not tipo_tarifa_bt:
                raise serializers.ValidationError({'tipo_tarifa_bt': 'Tipo de tarifa é obrigatório para BT.'})

            if tipo_tarifa_at:
                raise serializers.ValidationError({'tipo_tarifa_at': 'Tipo de tarifa AT não é permitido para BT.'})

        # Validações de Subgrupo AT
        if subgrupo == 'AT':
            if not tipo_tarifa_at:
                raise serializers.ValidationError({'tipo_tarifa_at': 'Tipo de tarifa é obrigatório para AT.'})

            if tipo_tarifa_bt:
                raise serializers.ValidationError({'tipo_tarifa_bt': 'Tipo de tarifa BT não é permitido para AT.'})

        return data


class TributoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tributo
        fields = '__all__'

