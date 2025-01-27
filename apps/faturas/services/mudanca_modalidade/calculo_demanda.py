from decimal import Decimal, InvalidOperation

from apps.faturas.models import Tributo
from apps.faturas.services.tarifa import buscar_tarifa_api


def calcular_demanda(conta_energia, modalidade, itens_fatura, posto_tarifario):
    demanda_total = Decimal(0)
    preco_unitario_local = Decimal(0)

    for item in itens_fatura:
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
            continue

        print(f"Tarifa Base Calculada: TUSD={tarifa['valor_tusd']}, TE={tarifa['valor_te']}")

        # Calcular tarifa base (TUSD + TE)
        tarifa_base = tarifa["valor_tusd"] + tarifa["valor_te"]
        print(f"Tarifa Base Calculada: {tarifa_base}")

        tributos = Tributo.objects.filter(conta_energia=conta_energia)
        pis = tributos.filter(tipo="PIS").first()
        cofins = tributos.filter(tipo="COFINS").first()
        icms = tributos.filter(tipo="ICMS").first()

        if not pis or not cofins or not icms:
            print("Tributos PIS, COFINS ou ICMS não encontrados.")
            continue

        # Calcular preço unitário
        preco_unitario_local = tarifa_base / (
                (1 - Decimal(pis.aliquota / 100) - Decimal(cofins.aliquota / 100)) /
                (1 - Decimal(icms.aliquota / 100))
        )

        print(f"Preço unitário calculado: {preco_unitario_local}")

        # Calcular demanda
        quantidade = Decimal(item.quantidade or 0)
        demanda = quantidade * preco_unitario_local
        print(f"Demanda para item {item.descricao}: {demanda}\n")

        demanda_total += demanda

    return demanda_total, preco_unitario_local, quantidade