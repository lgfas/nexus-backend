from decimal import Decimal, InvalidOperation
from io import StringIO

import pandas as pd
import requests
from django.db import transaction

from .models import Distribuidora, Tarifa


def processar_tarifas_csv(file):
    """
    Processa um arquivo CSV contendo tarifas elétricas, com suporte para arquivos locais e dados baixados de URLs públicas.
    """
    # Ler o CSV
    df = pd.read_csv(file, delimiter=',', encoding='utf-8')

    # Função para conversão segura de valores decimais
    def safe_decimal(value, column_name, index):
        try:
            # Substituir vírgulas por pontos e remover espaços extras
            value = str(value).replace(',', '.').strip()

            # Tratar valores vazios ou inválidos como 0.00
            if not value or value in ['.', ',', '']:
                return Decimal('0.00')

            # Converter para Decimal
            return Decimal(value)
        except (InvalidOperation, ValueError) as e:
            raise Exception(f"Erro ao converter '{value}' na coluna '{column_name}' (Linha {index + 1}): {e}")

    # Processar por blocos para otimizar
    block_size = 10000
    total_rows = len(df)

    # Lista para armazenar possíveis erros
    erros = []

    for start in range(0, total_rows, block_size):
        end = start + block_size
        block = df.iloc[start:end]  # Bloco atual

        # Usar transação para cada bloco
        with transaction.atomic():
            for index, row in block.iterrows():
                try:
                    # Buscar ou criar a distribuidora
                    distribuidora, _ = Distribuidora.objects.get_or_create(
                        codigo=str(row['NumCNPJDistribuidora']),
                        defaults={
                            'nome': str(row['SigAgente']),
                            'estado': str(row['SigAgenteAcessante'])
                        }
                    )

                    # Checar duplicatas antes de inserir
                    exists = Tarifa.objects.filter(
                        distribuidora=distribuidora,
                        data_inicio_vigencia=pd.to_datetime(row['DatInicioVigencia']),
                        modalidade=row['DscModalidadeTarifaria'],
                        subgrupo=row['DscSubGrupo'],
                        tipo_tarifa=row['DscBaseTarifaria']
                    ).exists()

                    if not exists:
                        Tarifa.objects.create(
                            distribuidora=distribuidora,
                            data_inicio_vigencia=pd.to_datetime(row['DatInicioVigencia']),
                            data_fim_vigencia=pd.to_datetime(row['DatFimVigencia']) if pd.notna(
                                row['DatFimVigencia']) else None,
                            modalidade=row['DscModalidadeTarifaria'],
                            subgrupo=row['DscSubGrupo'],
                            tipo_tarifa=row['DscBaseTarifaria'],
                            valor_te=safe_decimal(row['VlrTE'], 'VlrTE', index),
                            valor_tusd=safe_decimal(row['VlrTUSD'], 'VlrTUSD', index)
                        )
                except Exception as e:
                    # Registrar erro
                    erros.append(f"Erro na linha {index + 1}: {e}")
                    continue  # Ignorar linha problemática

    # Retornar status do processamento
    if erros:
        return {"status": "concluído com erros", "detalhes": erros[:10]}  # Limitar erros exibidos
    return {"status": "concluído"}


def processar_tarifas_url(url):
    """
    Processa tarifas baixadas diretamente de uma URL pública.
    """
    try:
        # Baixar dados do CSV via URL
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Erro ao acessar URL: {response.status_code}")

        # Carregar o CSV diretamente do texto baixado
        csv_file = StringIO(response.text)

        # Processar usando a mesma função de arquivo local
        resultado = processar_tarifas_csv(csv_file)
        return resultado
    except Exception as e:
        raise Exception(f"Erro ao processar URL: {e}")
