from decimal import Decimal

from apps.faturas.models import Tributo
from apps.faturas.services.tarifa import buscar_tarifa_api
from apps.historicos.models import HistoricoConsumoDemanda


def demanda_otima_verde_teste(conta_energia, demanda_contratada_unica_teste):

    demanda_contratada_unica = Decimal(demanda_contratada_unica_teste)

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

        print(f"\nDemanda: {demanda}"
              f"\nDemanda Isenta: {demanda_isenta}"
              f"\nDemanda Ultrapassagem: {demanda_ultrapassagem}"
              f"\nTotal {historico} R$ {total_rs}\n")

    print(f"Demanda Contratada Unica (kW): {demanda_contratada_unica}"
          f"\nValor total: R$ {total_rs}"
          f"\nMedia mensal: R$ {total_rs / Decimal(13)}"
          )

    return demanda_contratada_unica, total_rs

def demanda_otima_azul_teste(conta_energia, posto_tarifario):

    demanda_contratada_unica = Decimal('0')

    if posto_tarifario == "Ponta":
        demanda_contratada_unica = Decimal(250.0)

    if posto_tarifario == "Fora ponta":
        demanda_contratada_unica = Decimal(250.0)

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
        if posto_tarifario == "Fora ponta":
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

        print(f"\nDemanda: {demanda}"
              f"\nDemanda Isenta: {demanda_isenta}"
              f"\nDemanda Ultrapassagem: {demanda_ultrapassagem}"
              f"\nTotal {historico} R$ {total_rs}\n")

    print(f"Demanda Contratada {posto_tarifario} (kW): {demanda_contratada_unica}"
          f"\nValor total: R$ {total_rs}"
          f"\nMedia mensal: R$ {total_rs / Decimal(13)}"
          )

    return demanda_contratada_unica, total_rs