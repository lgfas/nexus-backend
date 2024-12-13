from rest_framework import viewsets

from .models import HistoricoConsumoDemanda
from .serializers import HistoricoConsumoDemandaSerializer


class HistoricoConsumoDemandaViewSet(viewsets.ModelViewSet):
    queryset = HistoricoConsumoDemanda.objects.all()
    serializer_class = HistoricoConsumoDemandaSerializer

