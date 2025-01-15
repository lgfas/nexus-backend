from decimal import Decimal
from django.db.models import Q

from apps.faturas.models import ItemFatura, Tributo
from apps.tarifas.models import Tarifa


def calcular_consumo_azul(conta_energia, modalidade="Azul"):
    """
    Calcula o consumo azul (consumo ponta e fora ponta) com base na conta de energia.
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
                # Recuperar a tarifa correspondente
                tarifa = Tarifa.objects.filter(
                    distribuidora=conta_energia.distribuidora,
                    modalidade=modalidade,
                    subgrupo=conta_energia.subgrupo,
                    tipo_tarifa="Tarifa de Aplicação",
                    nom_posto_tarifario=posto_tarifario,
                    data_inicio_vigencia__lte=conta_energia.data_vencimento
                ).order_by("-data_inicio_vigencia").first()

                if not tarifa:
                    raise ValueError(f"Tarifa não encontrada para o posto tarifário {posto_tarifario}.")

                # Calcular tarifa base (TUSD + TE)
                tarifa_base = tarifa.valor_tusd + tarifa.valor_te

                # Recuperar alíquotas de tributos
                tributos = Tributo.objects.filter(conta_energia=conta_energia)
                pis = tributos.filter(tipo="PIS").first()
                cofins = tributos.filter(tipo="CONFINS").first()
                icms = tributos.filter(tipo="ICMS").first()

                if not pis or not cofins or not icms:
                    raise ValueError("Tributos PIS, CONFINS ou ICMS não encontrados para a conta de energia.")

                # Calcular preço unitário
                preco_unitario = tarifa_base / (
                    (1 - Decimal(pis.aliquota / 100))
                    * (1 - Decimal(cofins.aliquota / 100))
                    * (1 - Decimal(icms.aliquota / 100))
                )

                # Calcular consumo
                quantidade = Decimal(item.quantidade or 0)
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
