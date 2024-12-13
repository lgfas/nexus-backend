import os

from PyPDF2 import PdfReader
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.historicos.models import HistoricoConsumoDemanda
from .models import ContaEnergia, ItensFatura
from .serializers import ContaEnergiaSerializer, ItensFaturaSerializer
from .utils import extract_fatura_data, extract_historico_data
from ..clientes.models import Cliente


class ContaEnergiaViewSet(viewsets.ModelViewSet):
    queryset = ContaEnergia.objects.all()
    serializer_class = ContaEnergiaSerializer

class ItensFaturaViewSet(viewsets.ModelViewSet):
    queryset = ItensFatura.objects.all()
    serializer_class = ItensFaturaSerializer

class UploadFaturaAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Capturar o ID do cliente na requisição
        cliente_id = request.data.get('cliente_id')
        if not cliente_id:
            return Response({"error": "O ID do cliente é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se o cliente existe
        try:
            cliente = Cliente.objects.get(id=cliente_id)
        except Cliente.DoesNotExist:
            return Response({"error": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Capturar o arquivo PDF enviado
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return Response({"error": "Nenhum arquivo enviado."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Salvar o arquivo temporariamente
            temp_path = f"/tmp/{pdf_file.name}"
            with open(temp_path, 'wb') as temp_file:
                for chunk in pdf_file.chunks():
                    temp_file.write(chunk)

            # Processar o PDF
            reader = PdfReader(temp_path)
            conta_data = extract_fatura_data(reader)

            # Criar ContaEnergia associada ao cliente
            conta = ContaEnergia.objects.create(
                cliente=cliente,
                mes=conta_data["mes"],
                vencimento=conta_data["vencimento"],
                total_pagar=conta_data["total_pagar"],
                leitura_anterior=conta_data["leitura_anterior"],
                leitura_atual=conta_data["leitura_atual"],
                numero_dias=conta_data["numero_dias"],
                proxima_leitura=conta_data["proxima_leitura"],
                demanda_contratada=conta_data["demanda_contratada"],
            )

            # Criar ItensFatura associados
            for item_data in conta_data["itens_fatura"]:
                ItensFatura.objects.create(
                    conta_energia=conta,
                    consumo_ponta=item_data["consumo_ponta"],
                    consumo_fora_ponta=item_data["consumo_fora_ponta"],
                    demanda_ativa=item_data["demanda_ativa"],
                    adicional_bandeira=item_data["adicional_bandeira"],
                )

            # Remover o arquivo temporário
            os.remove(temp_path)

            return Response({"message": "Dados processados e salvos com sucesso."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
