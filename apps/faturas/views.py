from rest_framework import viewsets

from .models import ContaEnergia, ItensFatura
from .serializers import ContaEnergiaSerializer, ItensFaturaSerializer


class ContaEnergiaViewSet(viewsets.ModelViewSet):
    queryset = ContaEnergia.objects.all()
    serializer_class = ContaEnergiaSerializer

class ItensFaturaViewSet(viewsets.ModelViewSet):
    queryset = ItensFatura.objects.all()
    serializer_class = ItensFaturaSerializer
