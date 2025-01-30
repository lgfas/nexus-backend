from decimal import Decimal, InvalidOperation

from apps.faturas.models import ItemFatura
from apps.faturas.services.demanda_otima_azul import encontrar_demanda_ideal_azul
from apps.faturas.services.mudanca_modalidade.calculo_demanda import calcular_tarifa_base_demanda, calcular_demandas
from apps.faturas.services.tarifa import buscar_tarifa_api, calcular_tarifas_com_impostos


def calcular_demanda_verde_para_azul_otimizada(conta_energia):
    """
    Calcula a demanda verde (demanda ativa, e demanda ultrapassagem) com base na conta de energia,
    utilizando a API da ANEEL para buscar tarifas.
    """

    tarifa_base_ponta_ci = Decimal(0)
    tarifa_ultrapassagem_ponta_ci = Decimal(0)
    tarifa_isenta_icms_ponta = Decimal(0)

    tarifa_base_fora_ponta_ci = Decimal(0)
    tarifa_ultrapassagem_fora_ponta_ci = Decimal(0)
    tarifa_isenta_icms_fora_ponta = Decimal(0)

    resultado_demanda = encontrar_demanda_ideal_azul(conta_energia)

    # Pegando os valores corretamente do dicionário
    demanda_contratada_ponta = resultado_demanda["melhor_demanda_ponta"]
    demanda_contratada_fora_ponta = resultado_demanda["melhor_demanda_fora_ponta"]

    # Depuração: imprimir valores antes da conversão
    print(
        f"Valores retornados por encontrar_demanda_ideal_azul: {demanda_contratada_ponta}, {demanda_contratada_fora_ponta}")

    # Garantir que os valores retornados sejam numéricos
    try:
        demanda_contratada_ponta = Decimal(str(demanda_contratada_ponta)) if demanda_contratada_ponta and str(
            demanda_contratada_ponta).replace('.', '', 1).isdigit() else Decimal(0)
        demanda_contratada_fora_ponta = Decimal(
            str(demanda_contratada_fora_ponta)) if demanda_contratada_fora_ponta and str(
            demanda_contratada_fora_ponta).replace('.', '', 1).isdigit() else Decimal(0)
    except InvalidOperation:
        raise ValueError(
            f"Erro ao converter demandas contratadas: {demanda_contratada_ponta}, {demanda_contratada_fora_ponta}"
        )

    print(f"Valores convertidos para Decimal: {demanda_contratada_ponta}, {demanda_contratada_fora_ponta}")


    tolerancia_ponta = demanda_contratada_ponta * Decimal(1.05)
    tolerancia_fora_ponta = demanda_contratada_fora_ponta * Decimal(1.05)

    item_fatura_ponta = ItemFatura.objects.filter(
        conta_energia=conta_energia,
        descricao__icontains="Demanda Ponta"
    ).first()

    item_fatura_fora_ponta = ItemFatura.objects.filter(
        conta_energia=conta_energia,
        descricao__icontains="Demanda Fora Ponta"
    ).first()

    quantidade_demanda_ponta = Decimal(item_fatura_ponta.quantidade) if item_fatura_ponta else Decimal(0)
    quantidade_demanda_fora_ponta = Decimal(item_fatura_fora_ponta.quantidade) if item_fatura_fora_ponta else Decimal(0)


    tarifa_base_ponta = calcular_tarifa_base_demanda(
        conta_energia=conta_energia,
        modalidade="Azul",
        posto_tarifario="Ponta"
    )

    tarifa_base_fora_ponta = calcular_tarifa_base_demanda(
        conta_energia=conta_energia,
        modalidade="Azul",
        posto_tarifario="Fora ponta"
    )

    tarifas_ponta_ci = calcular_tarifas_com_impostos(tarifa_base_ponta, conta_energia)
    tarifa_base_ponta_ci = tarifas_ponta_ci["tarifa_base_ci"]
    tarifa_ultrapassagem_ponta_ci = tarifas_ponta_ci["tarifa_ultrapassagem_ci"]
    tarifa_isenta_icms_ponta = tarifas_ponta_ci["tarifa_isenta_icms"]

    tarifas_fora_ponta_ci = calcular_tarifas_com_impostos(tarifa_base_fora_ponta, conta_energia)
    tarifa_base_fora_ponta_ci = tarifas_fora_ponta_ci["tarifa_base_ci"]
    tarifa_ultrapassagem_fora_ponta_ci = tarifas_fora_ponta_ci["tarifa_ultrapassagem_ci"]
    tarifa_isenta_icms_fora_ponta = tarifas_fora_ponta_ci["tarifa_isenta_icms"]

    demandas_ponta_rs = calcular_demandas(
        quantidade_demanda_ponta,
        demanda_contratada_ponta,
        tarifa_base_ponta_ci,
        tarifa_ultrapassagem_ponta_ci,
        tarifa_isenta_icms_ponta,
    )
    demanda_ponta_rs = demandas_ponta_rs["demanda_rs"]
    demanda_isenta_ponta_rs = demandas_ponta_rs["demanda_isenta_rs"]
    demanda_ultrapassagem_ponta_rs = demandas_ponta_rs["demanda_ultrapassagem_rs"]

    demandas_fora_ponta_rs = calcular_demandas(
        quantidade_demanda_fora_ponta,
        demanda_contratada_fora_ponta,
        tarifa_base_fora_ponta_ci,
        tarifa_ultrapassagem_fora_ponta_ci,
        tarifa_isenta_icms_fora_ponta,
    )
    demanda_fora_ponta_rs = demandas_fora_ponta_rs["demanda_rs"]
    demanda_isenta_fora_ponta_rs = demandas_fora_ponta_rs["demanda_isenta_rs"]
    demanda_ultrapassagem_fora_ponta_rs = demandas_fora_ponta_rs["demanda_ultrapassagem_rs"]

    print(f"\nDemanda Ponta: R$ {demanda_ponta_rs}"
          f"\nDemanda Isenta Ponta: R$ {demanda_isenta_ponta_rs}"
          f"\nDemanda Ultrapassagem Ponta: R$ {demanda_ultrapassagem_ponta_rs}")

    print(f"\nDemanda Fora Ponta: R$ {demanda_fora_ponta_rs}"
          f"\nDemanda Isenta Fora Ponta: R$ {demanda_isenta_fora_ponta_rs}"
          f"\nDemanda Ultrapassagem Fora Ponta: R$ {demanda_ultrapassagem_fora_ponta_rs}")

