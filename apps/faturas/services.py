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
                    data_vencimento=conta_energia.vencimento,
                    unidade="MWh"  # Unidade ajustada para API
                )

                print(f"Tarifa Base Calculada: TUSD={tarifa['valor_tusd']}, TE={tarifa['valor_te']}")

                if not tarifa:
                    print(f"Tarifa não encontrada para {posto_tarifario}.")
                    continue

                tarifa_base = ((tarifa["valor_tusd"]) / 1000) + ((tarifa["valor_te"]) / 1000)
                print(f"Tarifa Base Calculada: {tarifa_base}")

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
                print(f"Quantidade: {quantidade}")
                consumo = quantidade * preco_unitario
                print(f"Consumo para item {item.descricao}: {consumo}\n")

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


def calcular_demanda_azul_api(conta_energia, modalidade="Azul"):
    """
    Calcula a demanda azul (demanda ponta, fora ponta e excedente) com base na conta de energia,
    utilizando a API da ANEEL para buscar tarifas.
    """
    try:
        # Inicializar valores
        demanda_ponta_azul = Decimal(0)
        demanda_fora_ponta_azul = Decimal(0)
        excedente_ponta = Decimal(0)
        excedente_fora_ponta = Decimal(0)
        preco_unitario_ponta = Decimal(0)
        preco_unitario_fora_ponta = Decimal(0)
        quantidade_demanda_ponta = Decimal(0)
        quantidade_demanda_fora_ponta = Decimal(0)

        # Filtrar itens de fatura relacionados à demanda ponta e fora ponta
        itens_fatura_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia, descricao__icontains="Demanda Ponta"
        )

        itens_fatura_fora_ponta = ItemFatura.objects.filter(
            conta_energia=conta_energia, descricao__icontains="Demanda Fora Ponta"
        )

        # Função para calcular demanda
        def calcular_demanda(itens_fatura, posto_tarifario):
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

                # Recuperar tributos
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

        # Calcular demanda ponta
        demanda_ponta_azul, preco_unitario_ponta, quantidade_demanda_ponta = calcular_demanda(itens_fatura_ponta, posto_tarifario="Ponta")

        # Calcular demanda fora ponta
        demanda_fora_ponta_azul, preco_unitario_fora_ponta, quantidade_demanda_fora_ponta = calcular_demanda(itens_fatura_fora_ponta, posto_tarifario="Fora ponta")

        print(f"\nPreço unitário Ponta: {preco_unitario_ponta}")
        print(f"Preço unitário Fora Ponta: {preco_unitario_fora_ponta}")
        print(f"Demanda Contratada Única: {conta_energia.demanda_contratada_unica}\n")

        # Calcular excedente ponta
        if quantidade_demanda_ponta > conta_energia.demanda_contratada_unica:
            excedente_ponta = (quantidade_demanda_ponta - Decimal(conta_energia.demanda_contratada_unica)) * 2 * preco_unitario_ponta
        else:
            excedente_ponta = Decimal(0)

        # Calcular excedente fora ponta
        if quantidade_demanda_fora_ponta > conta_energia.demanda_contratada_unica:
            excedente_fora_ponta = (quantidade_demanda_fora_ponta - Decimal(conta_energia.demanda_contratada_unica)) * 2 * preco_unitario_fora_ponta
        else:
            excedente_fora_ponta = Decimal(0)

        print(f"\nExcedente Ponta: {excedente_ponta}")
        print(f"Excedente Fora Ponta: {excedente_fora_ponta}\n")

        # Calcular demanda total
        demanda_azul = demanda_ponta_azul + demanda_fora_ponta_azul + excedente_ponta + excedente_fora_ponta

        return {
            "demanda_ponta_azul": demanda_ponta_azul,
            "demanda_fora_ponta_azul": demanda_fora_ponta_azul,
            "excedente_ponta": excedente_ponta,
            "excedente_fora_ponta": excedente_fora_ponta,
            "demanda_azul": demanda_azul,
        }

    except Exception as e:
        raise ValueError(f"Erro ao calcular demanda azul: {e}")


def calcular_valor_total_azul(conta_energia, modalidade="Azul"):
    """
    Calcula o valor total azul considerando o consumo, demanda e os itens de fatura
    que não foram processados anteriormente para consumo e demanda.
    """
    try:
        # Calcular consumo azul
        consumo_data = calcular_consumo_azul_api(conta_energia, modalidade)
        consumo_azul = consumo_data["consumo_azul"]

        # Calcular demanda azul
        demanda_data = calcular_demanda_azul_api(conta_energia, modalidade)
        demanda_azul = demanda_data["demanda_azul"]

        # Descrições utilizadas no cálculo de consumo e demanda
        descricoes_utilizadas = [
            "Consumo Ponta (kWh)",
            "Consumo Fora Ponta (kWh)",
            "Demanda Ponta",
            "Demanda Fora Ponta",
            "Demanda Ativa (kW)",
            "Demanda Ultrapassagem (kW)"
        ]

        # Filtrar itens de fatura que não estão nas descrições utilizadas
        itens_restantes = ItemFatura.objects.filter(conta_energia=conta_energia).exclude(
            descricao__in=descricoes_utilizadas
        )

        # Somar os valores desses itens restantes
        valor_itens_restantes = sum(Decimal(item.valor or 0) for item in itens_restantes)

        # Calcular valor total azul
        valor_total_azul = consumo_azul + demanda_azul + valor_itens_restantes

        print(f"\nConsumo Azul: {consumo_azul}")
        print(f"\nDemanda Azul: {demanda_azul}")
        print(f"\nValor Itens Restantes: {valor_itens_restantes}")
        print(f"\nValor Total Azul: {valor_total_azul}")

        return {
            "consumo_azul": consumo_azul,
            "demanda_azul": demanda_azul,
            "valor_itens_restantes": valor_itens_restantes,
            "valor_total_azul": valor_total_azul,
        }

    except Exception as e:
        raise ValueError(f"Erro ao calcular valor total azul: {e}")