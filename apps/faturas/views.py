import os

from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ContaEnergia, ItemFatura
from .serializers import ContaEnergiaSerializer, ItemFaturaSerializer
from .utils import extract_itens_fatura, extract_historico_data
from ..clientes.models import Cliente
from ..historicos.models import HistoricoConsumoDemanda


class ContaEnergiaViewSet(viewsets.ModelViewSet):
    queryset = ContaEnergia.objects.all()
    serializer_class = ContaEnergiaSerializer

class ItemFaturaViewSet(viewsets.ModelViewSet):
    queryset = ItemFatura.objects.all()
    serializer_class = ItemFaturaSerializer

class UploadFaturaAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Receber IDs e arquivo
        conta_id = request.data.get('conta_energia_id')
        cliente_id = request.data.get('cliente_id')
        pdf_file = request.FILES.get('file')

        if not pdf_file:
            return Response({"error": "Nenhum arquivo enviado."}, status=status.HTTP_400_BAD_REQUEST)

        if not conta_id or not cliente_id:
            return Response({"error": "IDs da conta de energia e cliente são obrigatórios."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validar conta e cliente
        try:
            conta_energia = ContaEnergia.objects.get(id=conta_id)
            cliente = Cliente.objects.get(id=cliente_id)
        except ContaEnergia.DoesNotExist:
            return Response({"error": "Conta de energia não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        except Cliente.DoesNotExist:
            return Response({"error": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Salvar temporariamente o arquivo
            temp_path = f"/tmp/{pdf_file.name}"
            with open(temp_path, 'wb') as temp_file:
                for chunk in pdf_file.chunks():
                    temp_file.write(chunk)

            # Extrair dados
            itens_fatura = extract_itens_fatura(temp_path)
            historico_data = extract_historico_data(temp_path)

            # Salvar itens de fatura
            for item in itens_fatura:
                ItemFatura.objects.create(conta_energia=conta_energia, **item)

            # Salvar histórico
            for historico in historico_data:
                HistoricoConsumoDemanda.objects.create(cliente=cliente, **historico)

            # Remover arquivo temporário
            os.remove(temp_path)

            return Response({"message": "Dados processados e salvos com sucesso."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Erro ao processar o PDF: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
