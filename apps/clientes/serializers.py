from rest_framework import serializers
from validate_docbr import CNPJ

from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

    def validate_cnpj(self, value):
        cnpj_validator = CNPJ()
        if not cnpj_validator.validate(value):
            raise serializers.ValidationError('CNPJ inválido.')
        return value
