from rest_framework import serializers

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
            'id', 'cliente', 'distribuidora', 'mes', 'vencimento', 'total_pagar',
            'leitura_anterior', 'leitura_atual', 'proxima_leitura',
            'numero_dias', 'subgrupo', 'modalidade',
            'demanda_contratada_unica', 'demanda_contratada_ponta', 'demanda_contratada_fora_ponta',
            'fator_potencia',
        ]

    def validate(self, data):
        subgrupo = data.get('subgrupo')
        modalidade = data.get('modalidade')

        # Validar subgrupo e modalidade
        if subgrupo.startswith('A') and modalidade not in [
            'Azul', 'Azul ABRACE CATIVO', 'Azul ABRACE LIVRE',
            'Verde', 'Verde ABRACE CATIVO', 'Verde ABRACE LIVRE',
        ]:
            raise serializers.ValidationError({'modalidade': 'Modalidade inválida para o subgrupo de alta tensão.'})

        if subgrupo.startswith('B') and modalidade not in [
            'Branca', 'Convencional', 'Convencional ABRACE', 'Convencional pré-pagamento',
        ]:
            raise serializers.ValidationError({'modalidade': 'Modalidade inválida para o subgrupo de baixa tensão.'})

        return data

class TributoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tributo
        fields = '__all__'

