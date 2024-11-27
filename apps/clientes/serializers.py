from rest_framework import serializers
from .models import Cliente
from validate_docbr import CNPJ

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

    def validate_cnpj(self, value):
        cnpj_validator = CNPJ()
        if not cnpj_validator.validate(value):
            raise serializers.ValidationError('CNPJ inválido.')
        return value

    def validate(self, data):
        limite_min = data.get('limite_min')
        limite_max = data.get('limite_max')
        if limite_min is not None and limite_max is not None:
            if limite_min >= limite_max:
                raise serializers.ValidationError({
                    'limite_min': 'O limite mínimo deve ser menor que o limite máximo.',
                    'limite_max': 'O limite máximo deve ser maior que o limite mínimo.'
                })
        return data
