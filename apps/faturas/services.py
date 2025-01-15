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
    return {
        "valor_tusd": safe_decimal(tarifa.get("VlrTUSD")),
        "valor_te": safe_decimal(tarifa.get("VlrTE"))
    }


def calcular_consumo_azul_api(conta_energia, modalidade="Azul"):
    """
    Calcula o consumo azul (consumo ponta e fora ponta) com base na conta de energia,
    utilizando a API da ANEEL para buscar tarifas.
    """
    try:
        # Inicializa valores de consumo
        consumo_ponta_azul = Decimal(0)
        consumo_fora_ponta_azul = Decimal(0)

        # Filtrar itens de fatura relacionados ao consumo ponta e fora ponta
        itens_fatura_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia,
            descricao__icontains="Consumo Ponta"
        )

        itens_fatura_fora_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia,
            descricao__icontains="Consumo Fora Ponta"
        )

        def calcular_consumo(itens_fatura, posto_tarifario):
            consumo_total = Decimal(0)

            for item in itens_fatura:
                # Buscar tarifa na API
                tarifa = buscar_tarifa_api(
                    distribuidora=conta_energia.distribuidora.nome,
                    modalidade=modalidade,
                    subgrupo=conta_energia.subgrupo,
                    tipo_tarifa="Tarifa de Aplicação",
                    posto_tarifario=posto_tarifario,
                    data_vencimento=conta_energia.vencimento
                )

                if not tarifa:
                    raise ValueError(f"Tarifa não encontrada para o posto tarifário {posto_tarifario}.")

                # Calcular tarifa base (TUSD + TE)
                tarifa_base = tarifa["valor_tusd"] + tarifa["valor_te"]

                # Recuperar alíquotas de tributos
                tributos = Tributo.objects.filter(conta_energia=conta_energia)
                pis = tributos.filter(tipo="PIS").first()
                cofins = tributos.filter(tipo="COFINS").first()
                icms = tributos.filter(tipo="ICMS").first()

                if not pis or not cofins or not icms:
                    raise ValueError("Tributos PIS, COFINS ou ICMS não encontrados para a conta de energia.")

                # Calcular preço unitário
                preco_unitario = tarifa_base / (
                    (1 - safe_decimal(pis.aliquota, 0) / 100)
                    * (1 - safe_decimal(cofins.aliquota, 0) / 100)
                    * (1 - safe_decimal(icms.aliquota, 0) / 100)
                )

                # Calcular consumo
                quantidade = safe_decimal(item.quantidade, 0)
                consumo = quantidade * preco_unitario
                consumo_total += consumo

            return consumo_total

        # Calcular consumo ponta
        consumo_ponta_azul = calcular_consumo(itens_fatura_ponta, posto_tarifario="Ponta")

        # Calcular consumo fora ponta
        consumo_fora_ponta_azul = calcular_consumo(itens_fatura_fora_ponta, posto_tarifario="Fora ponta")

        # Retornar consumo total
        consumo_azul = consumo_ponta_azul + consumo_fora_ponta_azul
        return {
            "consumo_ponta_azul": consumo_ponta_azul,
            "consumo_fora_ponta_azul": consumo_fora_ponta_azul,
            "consumo_azul": consumo_azul,
        }

    except Exception as e:
        raise ValueError(f"Erro ao calcular consumo azul: {e}")

