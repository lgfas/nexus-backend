from decimal import Decimal, InvalidOperation

from apps.faturas.models import Tributo
from apps.faturas.services.tarifa import buscar_tarifa_api


def calcular_tarifa_base_demanda(conta_energia, modalidade, posto_tarifario):

    tarifa_base = Decimal(0)

    # Buscar tarifa na API (unidade kW)
    tarifa = buscar_tarifa_api(
        distribuidora=conta_energia.distribuidora.nome,
        modalidade=modalidade,
        subgrupo=conta_energia.subgrupo,
        tipo_tarifa="Tarifa de Aplicação",
        posto_tarifario=posto_tarifario,
        data_vencimento=conta_energia.vencimento,
        unidade="kW"  # Unidade ajustada para demanda
    )

    if not tarifa:
        print(f"Tarifa não encontrada para {posto_tarifario}.")

    print(f"Tarifa Base Calculada: TUSD={tarifa['valor_tusd']}, TE={tarifa['valor_te']}")

    # Calcular tarifa base (TUSD + TE)
    tarifa_base = tarifa["valor_tusd"] + tarifa["valor_te"]
    print(f"Tarifa Base Calculada: {tarifa_base}")

    return tarifa_base

def calcular_demandas(quantidade_demanda, demanda_contratada, tarifa_base_ci, tarifa_ultrapassagem_ci, tarifa_isenta_icms):
    """
    Calcula os valores das demandas contratadas, isentas e de ultrapassagem.
    """

    # Garantir que os valores são Decimal
    quantidade_demanda = Decimal(str(quantidade_demanda)) if not isinstance(quantidade_demanda, Decimal) else quantidade_demanda
    demanda_contratada = Decimal(str(demanda_contratada)) if not isinstance(demanda_contratada, Decimal) else demanda_contratada

    # Tolerância de 5%
    tolerancia = demanda_contratada * Decimal(1.05)

    # Inicializa valores
    demanda_ultrapassagem = Decimal(0)
    demanda_isenta = Decimal(0)

    # Condições para cálculo da demanda
    if quantidade_demanda < demanda_contratada:
        demanda_isenta = demanda_contratada - quantidade_demanda
    elif quantidade_demanda > tolerancia:
        demanda_ultrapassagem = quantidade_demanda - demanda_contratada

    # Cálculo dos valores em reais (R$)
    demanda_rs = quantidade_demanda * tarifa_base_ci
    demanda_isenta_rs = demanda_isenta * tarifa_isenta_icms
    demanda_ultrapassagem_rs = demanda_ultrapassagem * tarifa_ultrapassagem_ci

    # Depuração: Imprimir os valores calculados para verificação
    print(f"\n--- Cálculo de Demanda ---"
          f"\nQuantidade Demanda: {quantidade_demanda} kW"
          f"\nDemanda Contratada: {demanda_contratada} kW"
          f"\nTolerância (5% acima): {tolerancia} kW"
          f"\nDemanda Isenta: {demanda_isenta} kW"
          f"\nDemanda Ultrapassagem: {demanda_ultrapassagem} kW"
          f"\n---------------------------------")

    return {
        "demanda_rs": demanda_rs,
        "demanda_isenta_rs": demanda_isenta_rs,
        "demanda_ultrapassagem_rs": demanda_ultrapassagem_rs,
    }
