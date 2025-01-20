from .serializers import HistoricoConsumoDemandaSerializer

import os
import tempfile

from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .utils import extract_historico_data
from ..clientes.models import Cliente
from ..historicos.models import HistoricoConsumoDemanda

class HistoricoConsumoDemandaViewSet(viewsets.ModelViewSet):
    queryset = HistoricoConsumoDemanda.objects.all()
    serializer_class = HistoricoConsumoDemandaSerializer

class HistoricoAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Receber ID e arquivo
        cliente_id = request.data.get('cliente_id')
        pdf_file = request.FILES.get('file')

        # Validações iniciais
        if not pdf_file:
            return Response({"error": "Nenhum arquivo enviado."}, status=status.HTTP_400_BAD_REQUEST)

        if not cliente_id:
            return Response({"error": "ID do cliente é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        # Validar cliente
        try:
            cliente = Cliente.objects.get(id=cliente_id)
        except Cliente.DoesNotExist:
            return Response({"error": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Processar arquivo
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, pdf_file.name)

            with open(temp_path, 'wb') as temp_file:
                for chunk in pdf_file.chunks():
                    temp_file.write(chunk)

            # Extrair histórico
            historico_data = extract_historico_data(temp_path)

            # Salvar histórico
            for historico in historico_data:
                HistoricoConsumoDemanda.objects.create(cliente=cliente, **historico)

            os.remove(temp_path)  # Remover arquivo temporário
            return Response({"message": "Histórico processado e salvo com sucesso."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Erro ao processar o histórico: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
