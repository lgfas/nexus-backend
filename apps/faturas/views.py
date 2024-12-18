from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .models import ContaEnergia, ItemFatura, ItemFinanceiro
from .serializers import ContaEnergiaSerializer, ItemFaturaSerializer, ItemFinanceiroSerializer
from .utils import extract_itens_fatura, extract_historico_data
import os

from ..clientes.models import Cliente
from ..historicos.models import HistoricoConsumoDemanda


class ContaEnergiaViewSet(viewsets.ModelViewSet):
    queryset = ContaEnergia.objects.all()
    serializer_class = ContaEnergiaSerializer

class ItemFaturaViewSet(viewsets.ModelViewSet):
    queryset = ItemFatura.objects.all()
    serializer_class = ItemFaturaSerializer

class ItemFinanceiroViewSet(viewsets.ModelViewSet):
    queryset = ItemFinanceiro.objects.all()
    serializer_class = ItemFinanceiroSerializer

class UploadFaturaAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Obter IDs de Conta de Energia e Cliente
        conta_id = request.data.get('conta_energia_id')
        cliente_id = request.data.get('cliente_id')

        if not conta_id or not cliente_id:
            return Response(
                {"error": "IDs de conta de energia e cliente são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            conta_energia = ContaEnergia.objects.get(id=conta_id)
            cliente = Cliente.objects.get(id=cliente_id)
        except ContaEnergia.DoesNotExist:
            return Response({"error": "Conta de energia não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        except Cliente.DoesNotExist:
            return Response({"error": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Processar o arquivo PDF
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return Response({"error": "Nenhum arquivo enviado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Salvar o arquivo temporariamente
            temp_path = f"/tmp/{pdf_file.name}"
            with open(temp_path, 'wb') as temp_file:
                for chunk in pdf_file.chunks():
                    temp_file.write(chunk)

            # Extrair dados
            itens_fatura = extract_itens_fatura(temp_path)
            historico_data = extract_historico_data(temp_path)

            # Criar Itens de Fatura
            for item in itens_fatura:
                ItemFatura.objects.create(conta_energia=conta_energia, **item)

            # Criar Histórico de Consumo e Demanda
            for historico in historico_data:
                HistoricoConsumoDemanda.objects.create(cliente=cliente, **historico)

            # Remover arquivo temporário
            os.remove(temp_path)

            return Response({"message": "Dados processados e salvos com sucesso."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

