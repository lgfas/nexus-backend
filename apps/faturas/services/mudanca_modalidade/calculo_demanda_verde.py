from decimal import Decimal

from apps.faturas.models import ItemFatura
from apps.faturas.services.mudanca_modalidade.calculo_demanda import calcular_demanda


def calcular_demanda_verde_api(conta_energia):
    """
    Calcula a demanda verde (demanda ativa, e demanda ultrapassagem) com base na conta de energia,
    utilizando a API da ANEEL para buscar tarifas.
    """
    try:
        # Inicializar valores
        demanda_ativa = Decimal(0)
        demanda_ultrapassagem = Decimal(0)
        preco_unitario_demanda_ativa= Decimal(0)
        quantidade_demanda_ativa = Decimal(0)
        modalidade = "Verde"

        # Filtrar itens de fatura relacionados à demanda ponta e fora ponta
        itens_fatura_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia, descricao__icontains="Demanda Ativa"
        )

        itens_fatura_fora_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia, descricao__icontains="Demanda Ultrapassagem"
        )

        # Função para calcular demanda

        # Calcular demanda ponta
        demanda_ativa, preco_unitario_demanda_ativa, quantidade_demanda_ativa = calcular_demanda(conta_energia, modalidade, itens_fatura_ponta, posto_tarifario="Não se aplica")

        print(f"\nPreço unitário Demanda Ativa: {preco_unitario_demanda_ativa}")
        print(f"Demanda Contratada Única: {conta_energia.demanda_contratada_unica}\n")

        # Calcular demanda ultrapassagem
        if quantidade_demanda_ativa > conta_energia.demanda_contratada_unica:
            demanda_ultrapassagem = (quantidade_demanda_ativa - Decimal(conta_energia.demanda_contratada_unica)) * 2 * preco_unitario_demanda_ativa
        else:
            demanda_ultrapassagem = Decimal(0)

        print(f"\nDemanda Ativa: {demanda_ativa}")
        print(f"Demanda de Ultrapassagem: {demanda_ultrapassagem}\n")

        # Calcular demanda total
        demanda_verde = demanda_ativa + demanda_ultrapassagem

        return {
            "demanda_ativa": demanda_ativa,
            "demanda_ultrapassagem": demanda_ultrapassagem,
            "demanda_verde": demanda_verde,
        }

    except Exception as e:
        raise ValueError(f"Erro ao calcular demanda azul: {e}")