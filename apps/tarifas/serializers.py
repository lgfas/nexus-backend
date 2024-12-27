from rest_framework import serializers
from .models import Distribuidora, Tarifa


class DistribuidoraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Distribuidora
        fields = '__all__'


class TarifaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarifa
        fields = '__all__'
