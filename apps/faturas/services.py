from decimal import Decimal, InvalidOperation

import requests

from apps.faturas.models import ItemFatura, Tributo


def safe_decimal(value, default=Decimal(0)):
    """
    Converte um valor em Decimal de forma segura.
    """
    try:
        return Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return default


def buscar_tarifa_api(distribuidora, modalidade, subgrupo, tipo_tarifa, posto_tarifario, data_vencimento):
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
          AND "DatInicioVigencia" <= '{data_vencimento}'
        ORDER BY "DatInicioVigencia" DESC
        LIMIT 1
    """

    response = requests.get(base_url, params={"sql": sql_query})
    if response.status_code != 200:
        raise ValueError(f"Erro na API da ANEEL: {response.status_code} - {response.text}")

    result = response.json().get("result", {}).get("records", [])
    if not result:
        return None

    tarifa = result[0]  # Pega o primeiro resultado (mais recente)

    # Função para tratar valores
    def tratar_valor(valor):
        if not valor or valor.strip() == ",00":
            return Decimal(0)
        return Decimal(valor.replace(",", "."))

    return {
        "valor_tusd": tratar_valor(tarifa["VlrTUSD"]),
        "valor_te": tratar_valor(tarifa["VlrTE"]),
    }



def calcular_consumo_azul_api(conta_energia, modalidade="Azul"):
    """
    Calcula o consumo azul (consumo ponta e fora ponta) com base na conta de energia,
    utilizando a API da ANEEL para buscar tarifas.
    """
    try:
        consumo_ponta_azul = Decimal(0)
        consumo_fora_ponta_azul = Decimal(0)

        itens_fatura_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia, descricao__icontains="Consumo Ponta"
        )

        itens_fatura_fora_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia, descricao__icontains="Consumo Fora Ponta"
        )

        def calcular_consumo(itens_fatura, posto_tarifario):
            consumo_total = Decimal(0)

            for item in itens_fatura:
                tarifa = buscar_tarifa_api(
                    distribuidora=conta_energia.distribuidora.nome,
                    modalidade=modalidade,
                    subgrupo=conta_energia.subgrupo,
                    tipo_tarifa="Tarifa de Aplicação",
                    posto_tarifario=posto_tarifario,
                    data_vencimento=conta_energia.vencimento
                )

                print(f"Tarifa Base Calculada: TUSD={tarifa['valor_tusd']}, TE={tarifa['valor_te']}")

                if not tarifa:
                    print(f"Tarifa não encontrada para {posto_tarifario}.")
                    continue

                tarifa_base = ((tarifa["valor_tusd"]) / 100) + ((tarifa["valor_te"]) / 100)

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
                consumo = quantidade * preco_unitario
                print(f"Consumo para item {item.descricao}: {consumo}")

                consumo_total += consumo

            return consumo_total

        consumo_ponta_azul = calcular_consumo(itens_fatura_ponta, posto_tarifario="Ponta")
        consumo_fora_ponta_azul = calcular_consumo(itens_fatura_fora_ponta, posto_tarifario="Fora ponta")
        consumo_azul = consumo_ponta_azul + consumo_fora_ponta_azul

        return {
            "consumo_ponta_azul": consumo_ponta_azul,
            "consumo_fora_ponta_azul": consumo_fora_ponta_azul,
            "consumo_azul": consumo_azul,
        }

    except Exception as e:
        raise ValueError(f"Erro ao calcular consumo azul: {e}")


