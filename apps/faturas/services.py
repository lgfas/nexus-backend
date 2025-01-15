from apps.tarifas.models import Tarifa


def analisar_consumo(conta):
    """
    Analisa o consumo da conta de energia e determina se é mais vantajoso
    permanecer na modalidade atual (Verde) ou migrar para Azul.
    """
    # Buscar tarifas mais recentes com base no mês da conta
    tarifas_verdes = Tarifa.objects.filter(
        distribuidora=conta.distribuidora,
        modalidade_tarifaria="Verde",
        subgrupo=conta.subgrupo,
        tipo_tarifa="Tarifa de Aplicação",
        data_inicio_vigencia__lte=conta.mes
    ).order_by('-data_inicio_vigencia')

    tarifas_azuis = Tarifa.objects.filter(
        distribuidora=conta.distribuidora,
        modalidade_tarifaria="Azul",
        subgrupo=conta.subgrupo,
        tipo_tarifa="Tarifa de Aplicação",
        data_inicio_vigencia__lte=conta.mes
    ).order_by('-data_inicio_vigencia')

    tarifa_verde = tarifas_verdes.first()
    tarifa_azul = tarifas_azuis.first()

    if not tarifa_verde or not tarifa_azul:
        raise ValueError("Tarifas Verde e/ou Azul não encontradas para esta distribuidora e subgrupo.")

    # Calculando o preço unitário das tarifas
    pis_cofins = conta.tributos.filter(tipo="PIS").first().aliquota + conta.tributos.filter(tipo="COFINS").first().aliquota
    icms = conta.tributos.filter(tipo="ICMS").first().aliquota

    def calcular_preco_unitario(tarifa):
        return tarifa / (1 - pis_cofins) / (1 - icms)

    preco_unitario_verde = calcular_preco_unitario(tarifa_verde.valor_tusd + tarifa_verde.valor_te)
    preco_unitario_azul = calcular_preco_unitario(tarifa_azul.valor_tusd + tarifa_azul.valor_te)

    # Calculando consumo (Ponta e Fora Ponta)
    consumo_ponta = conta.itens_fatura.filter(descricao="Consumo Ponta (kWh)").first()
    consumo_fora_ponta = conta.itens_fatura.filter(descricao="Consumo Fora Ponta (kWh)").first()

    valor_consumo_verde = (
        consumo_ponta.quantidade * preco_unitario_verde +
        consumo_fora_ponta.quantidade * preco_unitario_verde
    )
    valor_consumo_azul = (
        consumo_ponta.quantidade * preco_unitario_azul +
        consumo_fora_ponta.quantidade * preco_unitario_azul
    )

    # Calculando demanda
    demanda_ativa = conta.itens_fatura.filter(descricao="Demanda Ativa (kW)").first()
    demanda_contratada = conta.demanda_contratada_unica
    demanda_excedente_verde = max(0, demanda_ativa.quantidade - demanda_contratada) * 2 * tarifa_verde.valor_te

    if demanda_contratada:
        demanda_ponta = conta.itens_fatura.filter(descricao="Demanda Ativa Isenta de ICMS (kW)").first()
        excedente_ponta = max(0, demanda_ponta.quantidade - demanda_contratada) * 2 * tarifa_azul.valor_te

        demanda_fora_ponta = consumo_fora_ponta.quantidade
        excedente_fora_ponta = max(0, demanda_fora_ponta - demanda_contratada) * 2 * tarifa_azul.valor_tusd

        demanda_excedente_azul = excedente_ponta + excedente_fora_ponta

    valor_demanda_verde = demanda_excedente_verde
    valor_demanda_azul = demanda_excedente_azul

    # Calculando o total
    total_verde = valor_consumo_verde + valor_demanda_verde
    total_azul = valor_consumo_azul + valor_demanda_azul

    # Comparando e retornando resultados
    resultado = "Verde" if total_verde < total_azul else "Azul"

    return {
        "tarifa_verde": {
            "valor_te": tarifa_verde.valor_te,
            "valor_tusd": tarifa_verde.valor_tusd,
            "preco_unitario": preco_unitario_verde,
        },
        "tarifa_azul": {
            "valor_te": tarifa_azul.valor_te,
            "valor_tusd": tarifa_azul.valor_tusd,
            "preco_unitario": preco_unitario_azul,
        },
        "consumo_verde": valor_consumo_verde,
        "consumo_azul": valor_consumo_azul,
        "demanda_verde": valor_demanda_verde,
        "demanda_azul": valor_demanda_azul,
        "total_verde": total_verde,
        "total_azul": total_azul,
        "melhor_opcao": resultado,
    }
