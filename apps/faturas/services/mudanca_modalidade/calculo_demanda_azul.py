from decimal import Decimal

from apps.faturas.models import ItemFatura
from apps.faturas.services.mudanca_modalidade.calculo_demanda import calcular_demanda


def calcular_demanda_azul_api(conta_energia):
    """
    Calcula a demanda azul (demanda ponta, fora ponta e excedente) com base na conta de energia,
    utilizando a API da ANEEL para buscar tarifas.
    """
    try:
        # Inicializar valores
        demanda_ponta_azul = Decimal(0)
        demanda_fora_ponta_azul = Decimal(0)
        excedente_ponta = Decimal(0)
        excedente_fora_ponta = Decimal(0)
        preco_unitario_ponta = Decimal(0)
        preco_unitario_fora_ponta = Decimal(0)
        quantidade_demanda_ponta = Decimal(0)
        quantidade_demanda_fora_ponta = Decimal(0)
        modalidade = "Azul"

        # Filtrar itens de fatura relacionados à demanda ponta e fora ponta
        itens_fatura_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia, descricao__icontains="Demanda Ponta"
        )

        itens_fatura_fora_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia, descricao__icontains="Demanda Fora Ponta"
        )

        # Função para calcular demanda

        # Calcular demanda ponta
        demanda_ponta_azul, preco_unitario_ponta, quantidade_demanda_ponta = calcular_demanda(conta_energia, modalidade, itens_fatura_ponta, posto_tarifario="Ponta")

        # Calcular demanda fora ponta
        demanda_fora_ponta_azul, preco_unitario_fora_ponta, quantidade_demanda_fora_ponta = calcular_demanda(conta_energia, modalidade, itens_fatura_fora_ponta, posto_tarifario="Fora ponta")

        print(f"\nPreço unitário Ponta: {preco_unitario_ponta}")
        print(f"Preço unitário Fora Ponta: {preco_unitario_fora_ponta}")
        print(f"Demanda Contratada Única: {conta_energia.demanda_contratada_unica}\n")

        # Calcular excedente ponta
        if quantidade_demanda_ponta > conta_energia.demanda_contratada_unica:
            excedente_ponta = (quantidade_demanda_ponta - Decimal(conta_energia.demanda_contratada_unica)) * 2 * preco_unitario_ponta
        else:
            excedente_ponta = Decimal(0)

        # Calcular excedente fora ponta
        if quantidade_demanda_fora_ponta > conta_energia.demanda_contratada_unica:
            excedente_fora_ponta = (quantidade_demanda_fora_ponta - Decimal(conta_energia.demanda_contratada_unica)) * 2 * preco_unitario_fora_ponta
        else:
            excedente_fora_ponta = Decimal(0)

        print(f"\nExcedente Ponta: {excedente_ponta}")
        print(f"Excedente Fora Ponta: {excedente_fora_ponta}\n")

        # Calcular demanda total
        demanda_azul = demanda_ponta_azul + demanda_fora_ponta_azul + excedente_ponta + excedente_fora_ponta

        return {
            "demanda_ponta_azul": demanda_ponta_azul,
            "demanda_fora_ponta_azul": demanda_fora_ponta_azul,
            "excedente_ponta": excedente_ponta,
            "excedente_fora_ponta": excedente_fora_ponta,
            "demanda_azul": demanda_azul,
        }

    except Exception as e:
        raise ValueError(f"Erro ao calcular demanda azul: {e}")