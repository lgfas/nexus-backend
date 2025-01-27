from decimal import Decimal

from apps.faturas.models import Tributo
from apps.faturas.services.tarifa import buscar_tarifa_api
from apps.historicos.models import HistoricoConsumoDemanda

def encontrar_demanda_ideal_azul(conta_energia):

    historico_conta = HistoricoConsumoDemanda.objects.filter(cliente=conta_energia.cliente)

    # Obter os valores possíveis para Ponta e Fora Ponta
    valores_ponta = sorted(set(historico.demanda_medida_ponta for historico in historico_conta))
    valores_fora_ponta = sorted(set(historico.demanda_medida_fora_ponta for historico in historico_conta))

    melhor_demanda_ponta = None
    melhor_demanda_fora_ponta = None
    menor_total_rs_ponta = Decimal('Infinity')
    menor_total_rs_fora_ponta = Decimal('Infinity')

    # Testar cada valor para Ponta
    for demanda_candidata in valores_ponta:
        conta_energia.demanda_contratada_unica = Decimal(demanda_candidata)
        total_rs = calcular_total_rs_azul(conta_energia, "Ponta")

        print(f"Demanda Contratada Unica Ponta: {demanda_candidata}, Total RS: {total_rs}")

        if total_rs < menor_total_rs_ponta:
            menor_total_rs_ponta = total_rs
            melhor_demanda_ponta = demanda_candidata

    # Testar cada valor para Fora Ponta
    for demanda_candidata in valores_fora_ponta:
        conta_energia.demanda_contratada_unica = Decimal(demanda_candidata)
        total_rs = calcular_total_rs_azul(conta_energia, "Fora ponta")

        print(f"Demanda Contratada Unica Fora ponta: {demanda_candidata}, Total RS: {total_rs}")

        if total_rs < menor_total_rs_fora_ponta:
            menor_total_rs_fora_ponta = total_rs
            melhor_demanda_fora_ponta = demanda_candidata

    print(f"\nMelhor Demanda Ponta: {melhor_demanda_ponta} kW - Menor Custo: R$ {menor_total_rs_ponta}")
    print(f"Melhor Demanda Fora Ponta: {melhor_demanda_fora_ponta} kW - Menor Custo: R$ {menor_total_rs_fora_ponta}")

    return {
        "melhor_demanda_ponta": melhor_demanda_ponta,
        "menor_total_rs_ponta": menor_total_rs_ponta,
        "melhor_demanda_fora_ponta": melhor_demanda_fora_ponta,
        "menor_total_rs_fora_ponta": menor_total_rs_fora_ponta,
    }


def calcular_total_rs_azul(conta_energia, posto_tarifario):

    '''
    O código é baseado no demanda_otima_azul
    Substitua por um cálculo simplificado que retorne apenas o `total_rs`
    Código original para calcular `total_rs` baseado no posto tarifário
    '''

    demanda_contratada_unica = Decimal(conta_energia.demanda_contratada_unica)
    tolerancia = demanda_contratada_unica * Decimal(1.05)

    demanda = Decimal(0)
    demanda_isenta = Decimal(0)
    demanda_ultrapassagem = Decimal(0)
    total_rs = Decimal(0)

    tarifa = buscar_tarifa_api(
        distribuidora=conta_energia.distribuidora.nome,
        modalidade="Azul",
        subgrupo=conta_energia.subgrupo,
        tipo_tarifa="Tarifa de Aplicação",
        posto_tarifario=posto_tarifario,
        data_vencimento=conta_energia.vencimento,
        unidade="kW"
    )

    tarifa_base = tarifa["valor_tusd"] + tarifa["valor_te"]

    tarifa_ultrapassagem = 2 * tarifa_base

    tributos = Tributo.objects.filter(conta_energia=conta_energia)

    pis = tributos.filter(tipo="PIS").first()
    cofins = tributos.filter(tipo="COFINS").first()
    icms = tributos.filter(tipo="ICMS").first()

    tarifa_base_ci = (tarifa_base /
                      (1 - Decimal(pis.aliquota / 100) - Decimal(cofins.aliquota / 100)) /
                      (1 - Decimal(icms.aliquota / 100))
                      )

    tarifa_ultrapassagem_ci = (tarifa_ultrapassagem /
                               (1 - Decimal(pis.aliquota / 100) - Decimal(cofins.aliquota / 100)) /
                               (1 - Decimal(icms.aliquota / 100))
                               )

    tarifa_isenta_icms = (tarifa_base /
                          (1 - Decimal(pis.aliquota / 100) - Decimal(cofins.aliquota / 100))
                          )

    print(f"\nTarifa Base Com Impostos: {tarifa_base_ci}"
          f"\nTarifa Ultrapassagem Com Impostos: {tarifa_ultrapassagem_ci}"
          f"\nTarifa Isenta ICMS: {tarifa_isenta_icms}\n")

    historico_conta = HistoricoConsumoDemanda.objects.filter(cliente=conta_energia.cliente)

    for historico in historico_conta:
        if posto_tarifario == "Ponta":
            demanda = historico.demanda_medida_ponta
        elif posto_tarifario == "Fora ponta":
            demanda = historico.demanda_medida_fora_ponta

        demanda = Decimal(demanda)

        if demanda < demanda_contratada_unica:
            demanda_isenta = demanda_contratada_unica - demanda
            demanda_ultrapassagem = 0
        else:
            demanda_isenta = 0
            if demanda > tolerancia:
                demanda_ultrapassagem = demanda - demanda_contratada_unica

        demanda_rs = demanda * tarifa_base_ci
        demanda_isenta_rs = demanda_isenta * tarifa_isenta_icms
        demanda_ultrapassagem_rs = demanda_ultrapassagem * tarifa_ultrapassagem_ci

        total_rs += demanda_rs + demanda_isenta_rs + demanda_ultrapassagem_rs

    return total_rs
