from rest_framework import serializers
from .models import ContaEnergia, ItensFatura
from apps.clientes.models import Cliente

class ItensFaturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItensFatura
        fields = '__all__'

class ContaEnergiaSerializer(serializers.ModelSerializer):
    itens_fatura = ItensFaturaSerializer(many=True, read_only=True)
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
            'itens_fatura',
        ]

    def validate(self, data):
        # Validar que leitura_atual >= leitura_anterior
        if data['leitura_atual'] < data['leitura_anterior']:
            raise serializers.ValidationError({
                'leitura_atual': 'A leitura atual não pode ser menor que a leitura anterior.'
            })
        # Validar que vencimento >= mes
        if data['vencimento'] < data['mes']:
            raise serializers.ValidationError({
                'vencimento': 'A data de vencimento não pode ser anterior ao mês de referência.'
            })
        # Validar que proxima_leitura > hoje
        if data['proxima_leitura'] <= date.today():
            raise serializers.ValidationError({
                'proxima_leitura': 'A data da próxima leitura deve ser futura.'
            })
        return data
