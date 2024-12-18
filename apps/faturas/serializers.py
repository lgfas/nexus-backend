from rest_framework import serializers
from .models import ContaEnergia, ItemFatura, ItemFinanceiro
from apps.clientes.models import Cliente

class ItemFaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemFatura
        fields = '__all__'

class ItemFinanceiroSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemFinanceiro
        fields = '__all__'

class ContaEnergiaSerializer(serializers.ModelSerializer):
    itens_fatura = ItemFaturaSerializer(many=True, read_only=True)
    itens_financeiros = ItemFinanceiroSerializer(many=True, read_only=True)
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
            'itens_financeiros',
        ]
