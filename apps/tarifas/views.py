from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Distribuidora, Tarifa
from .serializers import DistribuidoraSerializer, TarifaSerializer
from .utils import processar_tarifas_csv, processar_tarifas_api


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
    Atualiza tarifas via API pública da ANEEL.
    """
    def post(self, request, *args, **kwargs):
        try:
            base_url = "https://dadosabertos.aneel.gov.br/api/3/action/datastore_search"
            resource_id = "fcf2906c-7c32-4b9b-a637-054e7a5234f4"  # ID do recurso

            resultado = processar_tarifas_api(base_url, resource_id)
            return Response(resultado, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Erro ao atualizar tarifas: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
