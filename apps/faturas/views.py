from rest_framework import viewsets
from .models import ContaEnergia, ItensFatura
from .serializers import ContaEnergiaSerializer, ItensFaturaSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

class ContaEnergiaViewSet(viewsets.ModelViewSet):
    queryset = ContaEnergia.objects.all()
    serializer_class = ContaEnergiaSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

class ItensFaturaViewSet(viewsets.ModelViewSet):
    queryset = ItensFatura.objects.all()
    serializer_class = ItensFaturaSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
