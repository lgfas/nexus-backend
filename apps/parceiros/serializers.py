from rest_framework import serializers
from .models import Parceiro
from validate_docbr import CNPJ

class ParceiroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parceiro
        fields = '__all__'
        read_only_fields = ['id']

    def validate_cnpj(self, value):
        cnpj_validator = CNPJ()
        if not cnpj_validator.validate(value):
            raise serializers.ValidationError('CNPJ inválido.')
        return value

    def validate_telefone(self, value):
        import re
        pattern = r'^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError('Telefone inválido. Formato esperado: (00) 0000-0000 ou (00) 00000-0000.')
        return value
