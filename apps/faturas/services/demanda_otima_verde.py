from decimal import Decimal

from apps.faturas.services.tarifa import buscar_tarifa_api, calcular_tarifas_com_impostos
from apps.historicos.models import HistoricoConsumoDemanda


def encontrar_demanda_ideal_verde(conta_energia):

    historico_conta = HistoricoConsumoDemanda.objects.filter(cliente=conta_energia.cliente)

    # Obter os valores possíveis de demanda a partir do histórico
    valores_demanda = []
    for historico in historico_conta:
        valores_demanda.append(historico.demanda_medida_ponta)
        valores_demanda.append(historico.demanda_medida_fora_ponta)

    # Remover duplicatas e garantir que os valores estejam ordenados
    valores_demanda = sorted(set(valores_demanda))

    menor_total_rs = Decimal('Infinity')
    melhor_demanda = None

    # Testar cada valor de demanda como demanda_contratada_unica
    for demanda_candidata in valores_demanda:
        conta_energia.demanda_contratada_unica = Decimal(demanda_candidata)
        total_rs = calcular_total_rs_verde(conta_energia)

        print(f"Demanda Contratada Unica: {demanda_candidata}, Total RS: {total_rs}")

        # Verificar se o total atual é o menor encontrado
        if total_rs < menor_total_rs:
            menor_total_rs = total_rs
            melhor_demanda = demanda_candidata

    print(f"\nMelhor Demanda Contratada Unica: {melhor_demanda}")
    print(f"Menor Valor Total RS: R$ {menor_total_rs}")
    return melhor_demanda, menor_total_rs


def calcular_total_rs_verde(conta_energia):
    # Código da função `demanda_otima_verde`, ajustado para retornar o total_rs
    demanda_contratada_unica = Decimal(conta_energia.demanda_contratada_unica)

    tolerancia = demanda_contratada_unica * Decimal(1.05)

    demanda = Decimal(0)
    demanda_isenta = Decimal(0)
    demanda_ultrapassagem = Decimal(0)
    total_rs = Decimal(0)

    tarifa = buscar_tarifa_api(
        distribuidora=conta_energia.distribuidora.nome,
        modalidade=conta_energia.modalidade,
        subgrupo=conta_energia.subgrupo,
        tipo_tarifa="Tarifa de Aplicação",
        posto_tarifario="Não se aplica",
        data_vencimento=conta_energia.vencimento,
        unidade="kW"
    )

    tarifa_base = tarifa["valor_tusd"] + tarifa["valor_te"]

    tarifas = calcular_tarifas_com_impostos(tarifa_base, conta_energia)
    tarifa_base_ci = tarifas["tarifa_base_ci"]
    tarifa_ultrapassagem_ci = tarifas["tarifa_ultrapassagem_ci"]
    tarifa_isenta_icms = tarifas["tarifa_isenta_icms"]

    historico_conta = HistoricoConsumoDemanda.objects.filter(cliente=conta_energia.cliente)

    for historico in historico_conta:

        if historico.demanda_medida_ponta > historico.demanda_medida_fora_ponta:
            demanda = historico.demanda_medida_ponta
        else:
            demanda = historico.demanda_medida_fora_ponta

        demanda = Decimal(demanda)

        if demanda < demanda_contratada_unica:
            demanda_isenta = demanda_contratada_unica - demanda
            demanda_ultrapassagem = 0
        else:
            demanda_isenta = 0

            if demanda > tolerancia:
                demanda_ultrapassagem = demanda - demanda_contratada_unica

        demanda_isenta = Decimal(demanda_isenta)
        demanda_ultrapassagem = Decimal(demanda_ultrapassagem)

        demanda_rs = demanda * tarifa_base_ci
        demanda_isenta_rs = demanda_isenta * tarifa_isenta_icms
        demanda_ultrapassagem_rs = demanda_ultrapassagem * tarifa_ultrapassagem_ci

        total_rs += demanda_rs + demanda_isenta_rs + demanda_ultrapassagem_rs

    return total_rs
