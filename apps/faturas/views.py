import os
import tempfile

import chardet  # Para detectar a codificação
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from .models import ContaEnergia, ItemFatura, Tributo
from .serializers import ContaEnergiaSerializer, ItemFaturaSerializer, TributoSerializer
from .services.mudanca_modalidade.calculo_total import calcular_valor_total
from .utils import extract_itens_fatura, extract_historico_data, extract_tributos, extract_itens_fatura_generalizado
from ..clientes.models import Cliente
from ..historicos.models import HistoricoConsumoDemanda


class ContaEnergiaViewSet(viewsets.ModelViewSet):
    queryset = ContaEnergia.objects.all()
    serializer_class = ContaEnergiaSerializer


class ItemFaturaViewSet(viewsets.ModelViewSet):
    queryset = ItemFatura.objects.all()
    serializer_class = ItemFaturaSerializer


class TributoViewSet(viewsets.ModelViewSet):
    queryset = Tributo.objects.all()
    serializer_class = TributoSerializer


class UploadFaturaAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        # Receber IDs e arquivo
        conta_id = request.data.get('conta_energia_id')
        cliente_id = request.data.get('cliente_id')
        pdf_file = request.FILES.get('file')

        # Validações iniciais
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
            # Criar caminho temporário multiplataforma
            temp_dir = tempfile.gettempdir()  # Diretório temporário adequado ao sistema operacional
            safe_filename = "".join(x for x in pdf_file.name if x.isalnum() or x in "._-")  # Remove caracteres inválidos
            temp_path = os.path.join(temp_dir, safe_filename)

            # Salvar o arquivo temporário
            with open(temp_path, 'wb') as temp_file:
                for chunk in pdf_file.chunks():
                    temp_file.write(chunk)

            # Detectar codificação do arquivo
            with open(temp_path, 'rb') as file:
                raw_data = file.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'  # Detecta codificação ou usa UTF-8 como padrão

            # Processar o arquivo com a codificação detectada
            with open(temp_path, 'r', encoding=encoding, errors='ignore') as file:
                pdf_content = file.read()

            # Extrair dados (passando o caminho do arquivo para as funções existentes)
            itens_fatura = extract_itens_fatura(temp_path)
            historico_data = extract_historico_data(temp_path)
            tributos_data = extract_tributos(temp_path)

            # Salvar itens de fatura
            for item in itens_fatura:
                ItemFatura.objects.create(conta_energia=conta_energia, **item)

            # Salvar histórico
            for historico in historico_data:
                HistoricoConsumoDemanda.objects.create(cliente=cliente, **historico)

            # Salvar tributos
            for tributo in tributos_data:
                Tributo.objects.create(conta_energia=conta_energia, **tributo)

            # Remover arquivo temporário após processamento
            os.remove(temp_path)

            return Response({"message": "Dados processados e salvos com sucesso."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()  # Log detalhado do erro
            return Response(
                {
                    "error": f"Erro ao processar o PDF: {str(e)}",
                    "details": error_details,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class ItensFaturaAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        conta_id = request.data.get('conta_energia_id')
        pdf_file = request.FILES.get('file')

        # Validações iniciais
        if not pdf_file:
            return Response({"error": "Nenhum arquivo enviado."}, status=status.HTTP_400_BAD_REQUEST)

        if not conta_id:
            return Response({"error": "O ID da conta de energia é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        # Validar a conta de energia
        try:
            conta_energia = ContaEnergia.objects.get(id=conta_id)
        except ContaEnergia.DoesNotExist:
            return Response({"error": "Conta de energia não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Criar caminho temporário multiplataforma
            temp_dir = tempfile.gettempdir()
            safe_filename = "".join(x for x in pdf_file.name if x.isalnum() or x in "._-")  # Limpar caracteres inválidos
            temp_path = os.path.join(temp_dir, safe_filename)

            # Salvar o arquivo temporário
            with open(temp_path, 'wb') as temp_file:
                for chunk in pdf_file.chunks():
                    temp_file.write(chunk)

            # Extrair os itens da fatura
            itens_fatura = extract_itens_fatura_generalizado(temp_path)

            # Salvar os itens de fatura no banco de dados
            for item in itens_fatura:
                ItemFatura.objects.create(conta_energia=conta_energia, **item)

            # Remover o arquivo temporário
            os.remove(temp_path)

            return Response({"message": "Itens de fatura processados e salvos com sucesso."}, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return Response(
                {"error": f"Erro ao processar o PDF: {str(e)}", "details": error_details},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class CalcularMelhoriaModalidadeAPIView(APIView):
    def get(self, request, conta_id, *args, **kwargs):
        # Buscar a conta de energia pelo ID
        try:
            conta_energia = ContaEnergia.objects.get(id=conta_id)
        except ContaEnergia.DoesNotExist:
            return Response({"error": "Conta de energia não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Calcular para a modalidade alternativa
            resultado = calcular_valor_total(conta_energia)

            # Verificar qual modalidade é mais eficiente
            valor_atual = conta_energia.total_pagar
            valor_calculado = resultado["valor_total_calculado"]
            modalidade_atual = conta_energia.modalidade
            modalidade_alternativa = "Azul" if modalidade_atual == "Verde" else "Verde"

            # Mensagem de resposta
            mensagem = (
                f"Modalidade atual ({modalidade_atual}): R$ {valor_atual:.2f}. "
                f"Modalidade alternativa ({modalidade_alternativa}): R$ {valor_calculado:.2f}. "
            )
            if valor_calculado < valor_atual:
                mensagem += f"A mudança para {modalidade_alternativa} seria mais eficiente."
            else:
                mensagem += f"Permanecer na modalidade {modalidade_atual} é mais vantajoso."

            return Response({"mensagem": mensagem}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Erro ao calcular a modalidade mais eficiente.", "detalhes": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class CalcularMelhorConsumoAnualAPIView(APIView):
    """
    API para calcular o consumo anual e sugerir a modalidade mais eficiente.
    """

    def get(self, request, conta_id, *args, **kwargs):
        try:
            conta_energia = ContaEnergia.objects.get(id=conta_id)
        except ContaEnergia.DoesNotExist:
            return Response({"error": "Conta de energia não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        try:
            modalidade_atual = conta_energia.modalidade
            modalidade_alternativa = "Azul" if modalidade_atual == "Verde" else "Verde"

            consumo_atual = calcular_consumo_anual(conta_energia, modalidade_atual)
            consumo_alternativo = calcular_consumo_anual(conta_energia, modalidade_alternativa)

            mensagem = (
                f"Consumo anual na modalidade atual ({modalidade_atual}): R$ {consumo_atual:.2f}. "
                f"Consumo anual na modalidade alternativa ({modalidade_alternativa}): R$ {consumo_alternativo:.2f}. "
            )

            if consumo_alternativo < consumo_atual:
                mensagem += f"A mudança para {modalidade_alternativa} seria mais eficiente."
            else:
                mensagem += f"Permanecer na modalidade {modalidade_atual} é mais vantajoso."

            return Response({"mensagem": mensagem}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Erro ao calcular o consumo anual mais eficiente.", "detalhes": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

from rest_framework.views import APIView


class CalcularMelhorDemandaAPIView(APIView):
    """
    API para calcular a melhor demanda e sugerir a modalidade mais eficiente.
    """

    def get(self, request, conta_id, *args, **kwargs):
        try:
            conta_energia = ContaEnergia.objects.get(id=conta_id)
        except ContaEnergia.DoesNotExist:
            return Response({"error": "Conta de energia não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        try:
            modalidade_atual = conta_energia.modalidade
            modalidade_alternativa = "Azul" if modalidade_atual == "Verde" else "Verde"

            # Calcular demanda na modalidade atual
            if modalidade_atual == "Verde":
                melhor_demanda_atual, menor_total_rs_atual = encontrar_demanda_ideal_verde(conta_energia)
            else:
                demanda_azul = encontrar_demanda_ideal_azul(conta_energia)
                melhor_demanda_atual = (
                    demanda_azul["melhor_demanda_ponta"] + demanda_azul["melhor_demanda_fora_ponta"]
                )
                menor_total_rs_atual = (
                    demanda_azul["menor_total_rs_ponta"] + demanda_azul["menor_total_rs_fora_ponta"]
                )

            # Calcular demanda na modalidade alternativa
            if modalidade_alternativa == "Verde":
                melhor_demanda_alternativa, menor_total_rs_alternativa = encontrar_demanda_ideal_verde(conta_energia)
            else:
                demanda_azul = encontrar_demanda_ideal_azul(conta_energia)
                melhor_demanda_alternativa = (
                    demanda_azul["melhor_demanda_ponta"] + demanda_azul["melhor_demanda_fora_ponta"]
                )
                menor_total_rs_alternativa = (
                    demanda_azul["menor_total_rs_ponta"] + demanda_azul["menor_total_rs_fora_ponta"]
                )

            # Mensagem de comparação
            mensagem = (
                f"Demanda na modalidade atual ({modalidade_atual}): {melhor_demanda_atual} kW - "
                f"Custo: R$ {menor_total_rs_atual:.2f}. "
                f"Demanda na modalidade alternativa ({modalidade_alternativa}): {melhor_demanda_alternativa} kW - "
                f"Custo: R$ {menor_total_rs_alternativa:.2f}. "
            )

            if menor_total_rs_alternativa < menor_total_rs_atual:
                mensagem += f"A mudança para {modalidade_alternativa} seria mais eficiente."
            else:
                mensagem += f"Permanecer na modalidade {modalidade_atual} é mais vantajoso."

            return Response({"mensagem": mensagem}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Erro ao calcular a demanda mais eficiente.", "detalhes": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.faturas.models import ContaEnergia
from apps.faturas.services.consumo_anual import calcular_consumo_anual
from apps.faturas.services.demanda_otima_azul import encontrar_demanda_ideal_azul
from apps.faturas.services.demanda_otima_verde import encontrar_demanda_ideal_verde


class CalcularMelhorModalidadeAPIView(APIView):
    """
    API para calcular e comparar os custos totais (consumo + demanda)
    entre a modalidade atual e a alternativa.
    """

    def get(self, request, conta_id, *args, **kwargs):
        try:
            conta_energia = ContaEnergia.objects.get(id=conta_id)
        except ContaEnergia.DoesNotExist:
            return Response({"error": "Conta de energia não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        try:
            modalidade_atual = conta_energia.modalidade
            modalidade_alternativa = "Azul" if modalidade_atual == "Verde" else "Verde"

            # 🔹 Calcular consumo para ambas as modalidades
            consumo_atual = calcular_consumo_anual(conta_energia, modalidade_atual)
            consumo_alternativo = calcular_consumo_anual(conta_energia, modalidade_alternativa)

            # 🔹 Calcular demanda para a modalidade atual
            if modalidade_atual == "Verde":
                melhor_demanda_atual, menor_total_rs_atual = encontrar_demanda_ideal_verde(conta_energia)
            else:
                demanda_azul = encontrar_demanda_ideal_azul(conta_energia)
                melhor_demanda_atual = (
                    demanda_azul["melhor_demanda_ponta"] + demanda_azul["melhor_demanda_fora_ponta"]
                )
                menor_total_rs_atual = (
                    demanda_azul["menor_total_rs_ponta"] + demanda_azul["menor_total_rs_fora_ponta"]
                )

            # 🔹 Calcular demanda para a modalidade alternativa
            if modalidade_alternativa == "Verde":
                melhor_demanda_alternativa, menor_total_rs_alternativa = encontrar_demanda_ideal_verde(conta_energia)
            else:
                demanda_azul = encontrar_demanda_ideal_azul(conta_energia)
                melhor_demanda_alternativa = (
                    demanda_azul["melhor_demanda_ponta"] + demanda_azul["melhor_demanda_fora_ponta"]
                )
                menor_total_rs_alternativa = (
                    demanda_azul["menor_total_rs_ponta"] + demanda_azul["menor_total_rs_fora_ponta"]
                )

            # 🔹 Somar consumo e demanda para cada modalidade
            total_atual = consumo_atual + menor_total_rs_atual
            total_alternativo = consumo_alternativo + menor_total_rs_alternativa

            # 🔹 Gerar mensagem de resposta
            mensagem = (
                f"Modalidade atual ({modalidade_atual}): R$ {total_atual:.2f} "
                f"(Consumo: R$ {consumo_atual:.2f}, Demanda: R$ {menor_total_rs_atual:.2f}). "
                f"Modalidade alternativa ({modalidade_alternativa}): R$ {total_alternativo:.2f} "
                f"(Consumo: R$ {consumo_alternativo:.2f}, Demanda: R$ {menor_total_rs_alternativa:.2f}). "
            )

            if total_alternativo < total_atual:
                mensagem += f"A mudança para {modalidade_alternativa} seria mais eficiente."
            else:
                mensagem += f"Permanecer na modalidade {modalidade_atual} é mais vantajoso."

            return Response({"mensagem": mensagem}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": "Erro ao calcular a modalidade mais eficiente.", "detalhes": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
