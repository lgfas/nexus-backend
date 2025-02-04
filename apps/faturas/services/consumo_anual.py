from decimal import Decimal

from apps.faturas.models import Tributo
from apps.faturas.services.tarifa import buscar_tarifa_api
from apps.historicos.models import HistoricoConsumoDemanda


def calcular_consumo_anual(conta_energia, modalidade_analise):

    consumo_anual = Decimal(0)

    historico_conta = HistoricoConsumoDemanda.objects.filter(cliente=conta_energia.cliente)

    for historico in historico_conta:

        consumo_ponta = calcular_consumo_historico(
            conta_energia,
            modalidade_analise,
            historico.consumo_faturado_ponta_tot,
            "Ponta"
        )

        consumo_fora_ponta = calcular_consumo_historico(
            conta_energia,
            modalidade_analise,
            historico.consumo_faturado_fora_ponta,
            "Fora ponta"
        )

        consumo_anual += Decimal(consumo_ponta) + Decimal(consumo_fora_ponta)

    print(f"Consumo Anual {modalidade_analise}: R$ {consumo_anual}")

    return consumo_anual

def calcular_consumo_historico(conta_energia, modalidade, historico_valor, posto_tarifario):
    consumo_total = Decimal(0)

    tarifa = buscar_tarifa_api(
        distribuidora=conta_energia.distribuidora.nome,
        modalidade=modalidade,
        subgrupo=conta_energia.subgrupo,
        tipo_tarifa="Tarifa de Aplicação",
        posto_tarifario=posto_tarifario,
        data_vencimento=conta_energia.vencimento,
        unidade="MWh"  # Unidade ajustada para API
    )

    print(f"\nTarifa Base Calculada: TUSD={tarifa['valor_tusd']}, TE={tarifa['valor_te']}")

    if not tarifa:
        print(f"Tarifa não encontrada para {posto_tarifario}.")

    tarifa_base = ((tarifa["valor_tusd"]) / 1000) + ((tarifa["valor_te"]) / 1000)
    print(f"Tarifa Base Calculada: {tarifa_base}")

    tributos = Tributo.objects.filter(conta_energia=conta_energia)
    pis = tributos.filter(tipo="PIS").first()
    cofins = tributos.filter(tipo="COFINS").first()
    icms = tributos.filter(tipo="ICMS").first()

    if not pis or not cofins or not icms:
        print("Tributos PIS, COFINS ou ICMS não encontrados.")

    preco_unitario = (tarifa_base /
                      (1 - Decimal(pis.aliquota / 100) - Decimal(cofins.aliquota / 100)) /
                      (1 - Decimal(icms.aliquota / 100))
                      )
    print(f"Preço unitário calculado: {preco_unitario}")

    quantidade = Decimal(historico_valor or 0)
    print(f"Quantidade: {quantidade}")
    consumo_total = quantidade * preco_unitario

    print(f"Consumo Total: R$ {consumo_total}\n")

    return consumo_total