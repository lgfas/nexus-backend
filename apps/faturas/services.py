from decimal import Decimal

def analisar_consumo(conta, tipo_tarifa_desejado):
    # Busca tarifas mais recentes para Verde e Azul
    tarifas_verde = conta.distribuidora.tarifas.filter(
        subgrupo=conta.subgrupo,
        modalidade="Verde",
        tipo_tarifa=tipo_tarifa_desejado,
        data_inicio_vigencia__lte=conta.mes,
    ).order_by('-data_inicio_vigencia').first()

    tarifas_azul = conta.distribuidora.tarifas.filter(
        subgrupo=conta.subgrupo,
        modalidade="Azul",
        tipo_tarifa=tipo_tarifa_desejado,
        data_inicio_vigencia__lte=conta.mes,
    ).order_by('-data_inicio_vigencia').first()

    if not tarifas_verde or not tarifas_azul:
        raise ValueError("Não foram encontradas tarifas para comparação nas modalidades Verde e Azul.")

    # Consumo e demanda
    consumo_ponta = Decimal(6426.0)  # Do PDF
    consumo_fora_ponta = Decimal(42994.8)  # Do PDF
    demanda_unica = Decimal(300.0)  # Demanda contratada única

    # Cálculo para Verde
    custo_verde = (
        (demanda_unica * tarifas_verde.valor_tusd) +
        ((consumo_ponta + consumo_fora_ponta) * tarifas_verde.valor_te)
    )

    # Cálculo para Azul
    demanda_ponta = consumo_ponta
    demanda_fora_ponta = consumo_fora_ponta
    custo_azul = (
        (demanda_ponta * tarifas_azul.valor_tusd) +
        (demanda_fora_ponta * tarifas_azul.valor_tusd) +
        (consumo_ponta * tarifas_azul.valor_te) +
        (consumo_fora_ponta * tarifas_azul.valor_te)
    )

    # Adiciona tributos
    tributos_total = Decimal(13076.63 + 308.70 + 1423.07)  # ICMS + PIS + COFINS
    custo_verde += tributos_total
    custo_azul += tributos_total

    # Resultado
    melhor_opcao = "Verde" if custo_verde < custo_azul else "Azul"

    return {
        "tarifa_verde": {
            "tipo_tarifa": tipo_tarifa_desejado,
            "valor_te": tarifas_verde.valor_te,
            "valor_tusd": tarifas_verde.valor_tusd,
            "custo_total": float(custo_verde),
        },
        "tarifa_azul": {
            "tipo_tarifa": tipo_tarifa_desejado,
            "valor_te": tarifas_azul.valor_te,
            "valor_tusd": tarifas_azul.valor_tusd,
            "custo_total": float(custo_azul),
        },
        "melhor_opcao": melhor_opcao,
    }
