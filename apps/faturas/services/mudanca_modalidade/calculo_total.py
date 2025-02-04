from decimal import Decimal

from apps.faturas.models import ItemFatura
from apps.faturas.services.mudanca_modalidade.calculo_consumo import calcular_consumo_api
from apps.faturas.services.mudanca_modalidade.demanda_azul_para_verde import calcular_demanda_azul_para_verde_otimizada
from apps.faturas.services.mudanca_modalidade.demanda_verde_para_azul import calcular_demanda_verde_para_azul_otimizada


def calcular_valor_total(conta_energia):
    """
    Calcula o valor total azul considerando o consumo, demanda e os itens de fatura
    que não foram processados anteriormente para consumo e demanda.
    """
    try:

        consumo = Decimal(0)
        demanda = Decimal(0)
        modalidade_analise = ''

        if conta_energia.modalidade == "Verde":
            # Calcular consumo azul
            modalidade_analise = "Azul"
            consumo_data = calcular_consumo_api(conta_energia,modalidade_analise)
            consumo = consumo_data["consumo"]

            # Calcular demanda azul
            demanda_data = calcular_demanda_verde_para_azul_otimizada(conta_energia)
            demanda = (
                    demanda_data["demanda_ponta_rs"] +
                    demanda_data["demanda_isenta_ponta_rs"] +
                    demanda_data["demanda_ultrapassagem_ponta_rs"] +
                    demanda_data["demanda_fora_ponta_rs"] +
                    demanda_data["demanda_isenta_fora_ponta_rs"] +
                    demanda_data["demanda_ultrapassagem_fora_ponta_rs"]
            )

            print(f"Total da Demanda: R$ {demanda}")

        if conta_energia.modalidade == "Azul":
            # Calcular consumo verde
            modalidade_analise = "Verde"
            consumo_data = calcular_consumo_api(conta_energia,modalidade_analise)
            consumo = consumo_data["consumo"]

            # Calcular demanda verde
            demanda_data = calcular_demanda_azul_para_verde_otimizada(conta_energia)
            demanda = (
                    demanda_data["demanda_ativa_rs"] +
                    demanda_data["demanda_isenta_icms_rs"] +
                    demanda_data["demanda_ultrapassagem_rs"]
            )

            print(f"Total da Demanda: R$ {demanda}")

        # Descrições utilizadas no cálculo de consumo e demanda
        descricoes_utilizadas = [
            "Consumo Ponta (kWh)",
            "Consumo Fora Ponta (kWh)",
            "Demanda Ponta",
            "Demanda Fora Ponta",
            "Demanda Ativa (kW)",
            "Demanda Ultrapassagem (kW)",
            "Demanda Ponta Isenta ICMS(kW)",
            "Demanda Fora Ponta Isenta ICMS(kW)"
        ]

        # Filtrar itens de fatura que não estão nas descrições utilizadas
        itens_restantes = ItemFatura.objects.filter(conta_energia=conta_energia).exclude(
            descricao__in=descricoes_utilizadas
        )

        # Somar os valores desses itens restantes
        valor_itens_restantes = sum(Decimal(item.valor or 0) for item in itens_restantes)

        # Calcular valor total azul
        valor_total_calculado = consumo + demanda + valor_itens_restantes

        print(f"\nConsumo {modalidade_analise}: {consumo}")
        print(f"\nDemanda {modalidade_analise}: {demanda}")
        print(f"\nValor Itens Restantes: {valor_itens_restantes}")
        print(f"\nValor Total {modalidade_analise}: {valor_total_calculado}")

        return {
            "consumo": consumo,
            "demanda": demanda,
            "valor_itens_restantes": valor_itens_restantes,
            "valor_total_calculado": valor_total_calculado,
        }

    except Exception as e:
        raise ValueError(f"Erro ao calcular valor total {modalidade_analise}: {e}")