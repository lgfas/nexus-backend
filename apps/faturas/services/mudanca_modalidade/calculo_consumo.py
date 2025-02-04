from decimal import Decimal

from apps.faturas.models import Tributo, ItemFatura
from apps.faturas.services.tarifa import buscar_tarifa_api


def calcular_consumo(conta_energia, modalidade, itens_fatura, posto_tarifario):
    consumo_total = Decimal(0)

    for item in itens_fatura:
        tarifa = buscar_tarifa_api(
            distribuidora=conta_energia.distribuidora.nome,
            modalidade=modalidade,
            subgrupo=conta_energia.subgrupo,
            tipo_tarifa="Tarifa de Aplicação",
            posto_tarifario=posto_tarifario,
            data_vencimento=conta_energia.vencimento,
            unidade="MWh"  # Unidade ajustada para API
        )

        print(f"Tarifa Base Calculada: TUSD={tarifa['valor_tusd']}, TE={tarifa['valor_te']}")

        if not tarifa:
            print(f"Tarifa não encontrada para {posto_tarifario}.")
            continue

        tarifa_base = ((tarifa["valor_tusd"]) / 1000) + ((tarifa["valor_te"]) / 1000)
        print(f"Tarifa Base Calculada: {tarifa_base}")

        tributos = Tributo.objects.filter(conta_energia=conta_energia)
        pis = tributos.filter(tipo="PIS").first()
        cofins = tributos.filter(tipo="COFINS").first()
        icms = tributos.filter(tipo="ICMS").first()

        if not pis or not cofins or not icms:
            print("Tributos PIS, COFINS ou ICMS não encontrados.")
            continue

        preco_unitario = (tarifa_base /
                          (1 - Decimal(pis.aliquota / 100) - Decimal(cofins.aliquota / 100)) /
                          (1 - Decimal(icms.aliquota / 100))
                          )
        print(f"Preço unitário calculado: {preco_unitario}")

        quantidade = Decimal(item.quantidade or 0)
        print(f"Quantidade: {quantidade}")
        consumo = quantidade * preco_unitario
        print(f"Consumo para item {item.descricao}: {consumo}\n")

        consumo_total += consumo

    return consumo_total

def calcular_consumo_api(conta_energia, modalidade_analise):
    """
    Calcula o consumo (consumo ponta e fora ponta) com base na conta de energia e na sua modalidade,
    utilizando a API da ANEEL para buscar tarifas.
    """
    try:
        consumo_ponta = Decimal(0)
        consumo_fora_ponta = Decimal(0)

        itens_fatura_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia, descricao__icontains="Consumo Ponta"
        )

        itens_fatura_fora_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia, descricao__icontains="Consumo Fora Ponta"
        )

        consumo_ponta = calcular_consumo(conta_energia, modalidade_analise, itens_fatura_ponta, posto_tarifario="Ponta")
        consumo_fora_ponta = calcular_consumo(conta_energia, modalidade_analise, itens_fatura_fora_ponta, posto_tarifario="Fora ponta")
        consumo = consumo_ponta + consumo_fora_ponta

        return {
            "consumo_ponta": consumo_ponta,
            "consumo_fora_ponta": consumo_fora_ponta,
            "consumo": consumo,
        }

    except Exception as e:
        raise ValueError(f"Erro ao calcular consumo: {e}")