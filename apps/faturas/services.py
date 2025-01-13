def analisar_consumo(conta, tipo_tarifa_desejado):
    distribuidora = conta.distribuidora

    # Buscar tarifas válidas para a distribuidora, subgrupo e modalidade
    tarifas_vigentes = distribuidora.tarifas.filter(
        data_inicio_vigencia__lte=conta.mes,
        subgrupo=conta.subgrupo,
        modalidade=conta.modalidade,
        tipo_tarifa=tipo_tarifa_desejado
    ).order_by('-data_inicio_vigencia')

    # Verificar se há tarifas disponíveis
    if not tarifas_vigentes.exists():
        raise ValueError(f"Não há tarifas do tipo '{tipo_tarifa_desejado}' vigentes para esta conta.")

    # Obter a tarifa mais recente
    tarifa_selecionada = tarifas_vigentes.first()

    # Cálculos de consumo
    consumo_ponta = (
        conta.itens_fatura.filter(descricao__icontains="Consumo Ponta (kWh)").first().quantidade or 0
    )
    consumo_fora_ponta = (
        conta.itens_fatura.filter(descricao__icontains="Consumo Fora Ponta (kWh)").first().quantidade or 0
    )

    # Cálculo de custo total
    custo_total = (
        (consumo_ponta + consumo_fora_ponta) * tarifa_selecionada.valor_te
    ) + tarifa_selecionada.valor_tusd

    # Retornar os detalhes
    return {
        "tarifa": {
            "tipo_tarifa": tipo_tarifa_desejado,
            "modalidade": conta.modalidade,
            "subgrupo": conta.subgrupo,
            "valor_te": tarifa_selecionada.valor_te,
            "valor_tusd": tarifa_selecionada.valor_tusd,
        },
        "consumo": {
            "ponta": consumo_ponta,
            "fora_ponta": consumo_fora_ponta,
        },
        "custo_total": custo_total,
    }
