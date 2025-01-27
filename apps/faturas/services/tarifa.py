from decimal import Decimal

import requests

from apps.faturas.models import Tributo


def buscar_tarifa_api(distribuidora, modalidade, subgrupo, tipo_tarifa, posto_tarifario, data_vencimento, unidade, detalhe="Não se aplica"):
    """
    Consulta a API da ANEEL para buscar a tarifa mais recente com base nos filtros fornecidos.
    """
    base_url = "https://dadosabertos.aneel.gov.br/api/3/action/datastore_search_sql"
    resource_id = "fcf2906c-7c32-4b9b-a637-054e7a5234f4"

    sql_query = f"""
            SELECT * 
            FROM "{resource_id}"
            WHERE "SigAgente" = '{distribuidora}'
              AND "DscModalidadeTarifaria" = '{modalidade}'
              AND "DscSubGrupo" = '{subgrupo}'
              AND "DscBaseTarifaria" = '{tipo_tarifa}'
              AND "NomPostoTarifario" = '{posto_tarifario}'
              AND "DscUnidadeTerciaria" = '{unidade}'
              AND "DatInicioVigencia" <= '{data_vencimento}'
              AND "DscDetalhe" = '{detalhe}'
            ORDER BY "DatInicioVigencia" DESC
            LIMIT 1
        """

    response = requests.get(base_url, params={"sql": sql_query})
    if response.status_code != 200:
        raise ValueError(f"Erro na API da ANEEL: {response.status_code} - {response.text}")

    result = response.json().get("result", {}).get("records", [])
    if not result:
        return None

    tarifa = result[0]

    # Função para tratar valores
    def tratar_valor(valor):
        if not valor or valor.strip() == ",00":
            return Decimal(0)
        return Decimal(valor.replace(",", "."))

    return {
        "valor_tusd": tratar_valor(tarifa["VlrTUSD"]),
        "valor_te": tratar_valor(tarifa["VlrTE"]),
    }

def calcular_tarifas_com_impostos(tarifa_base, conta_energia):

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

    return {
        "tarifa_base_ci": Decimal(tarifa_base_ci),
        "tarifa_ultrapassagem_ci": Decimal(tarifa_ultrapassagem_ci),
        "tarifa_isenta_icms": Decimal(tarifa_isenta_icms)
    }