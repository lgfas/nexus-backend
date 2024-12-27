from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Distribuidora, Tarifa
from .serializers import DistribuidoraSerializer, TarifaSerializer
from .utils import processar_tarifas_csv, processar_tarifas_url


class DistribuidoraViewSet(viewsets.ModelViewSet):
    queryset = Distribuidora.objects.all()
    serializer_class = DistribuidoraSerializer


class TarifaViewSet(viewsets.ModelViewSet):
    queryset = Tarifa.objects.all()
    serializer_class = TarifaSerializer


class UploadTarifasCSVAPIView(APIView):
    """
    Processa tarifas enviadas por arquivos CSV.
    """
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({"error": "Nenhum arquivo CSV enviado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resultado = processar_tarifas_csv(csv_file)
            return Response(resultado, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Erro ao processar o arquivo: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class AtualizarTarifasAPIView(APIView):
    """
    Atualiza tarifas via URL pública.
    """
    def post(self, request, *args, **kwargs):
        try:
            # URL pública fornecida
            url = "https://dadosabertos.aneel.gov.br/path/to/tarifas.csv"  # Atualizar com URL válida
            resultado = processar_tarifas_url(url)

            return Response(resultado, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Erro ao atualizar tarifas: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
