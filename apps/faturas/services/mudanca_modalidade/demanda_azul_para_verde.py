from decimal import Decimal

from apps.faturas.models import ItemFatura
from apps.faturas.services.demanda_otima_verde import encontrar_demanda_ideal_verde
from apps.faturas.services.mudanca_modalidade.calculo_demanda import calcular_tarifa_base_demanda, calcular_demandas
from apps.faturas.services.tarifa import calcular_tarifas_com_impostos


def calcular_demanda_azul_para_verde_otimizada(conta_energia):
    """
    Calcula a demanda azul (demanda ponta, fora ponta e excedente) com base na conta de energia,
    utilizando a API da ANEEL para buscar tarifas.
    """

    quantidade_demanda_ativa = Decimal(0)

    tarifa_base_demanda_ativa_ci = Decimal(0)
    tarifa_ultrapassagem_demanda_ativa_ci = Decimal(0)
    tarifa_isenta_icms_demanda_ativa = Decimal(0)

    demanda_contratada_unica, _ = encontrar_demanda_ideal_verde(conta_energia)

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

    if quantidade_demanda_ponta > quantidade_demanda_fora_ponta:
        quantidade_demanda_ativa = quantidade_demanda_ponta
    else:
        quantidade_demanda_ativa = quantidade_demanda_fora_ponta

    tarifa_base_demanda_ativa = calcular_tarifa_base_demanda(
        conta_energia=conta_energia,
        modalidade="Verde",
        posto_tarifario="Não se aplica"
    )

    tarifas_demanda_ativa_ci = calcular_tarifas_com_impostos(
        tarifa_base_demanda_ativa,
        conta_energia=conta_energia,
    )

    tarifa_base_demanda_ativa_ci = tarifas_demanda_ativa_ci["tarifa_base_ci"]
    tarifa_ultrapassagem_demanda_ativa_ci = tarifas_demanda_ativa_ci["tarifa_ultrapassagem_ci"]
    tarifa_isenta_icms_demanda_ativa = tarifas_demanda_ativa_ci["tarifa_isenta_icms"]

    demandas_rs = calcular_demandas(
        quantidade_demanda_ativa,
        demanda_contratada_unica,
        tarifa_base_demanda_ativa_ci,
        tarifa_ultrapassagem_demanda_ativa_ci,
        tarifa_isenta_icms_demanda_ativa,
    )

    demanda_ativa_rs = demandas_rs["demanda_rs"]
    demanda_ultrapassagem_rs = demandas_rs["demanda_ultrapassagem_rs"]
    demanda_isenta_icms_rs = demandas_rs["demanda_isenta_rs"]

    print(f"\nDemanda Ativa: R$ {demanda_ativa_rs}"
          f"\nDemanda Isenta ICMS: R$ {demanda_isenta_icms_rs}"
          f"\nDemanda Ultrapassagem: R$ {demanda_ultrapassagem_rs}")
