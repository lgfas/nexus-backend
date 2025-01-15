from decimal import Decimal, InvalidOperation
from io import StringIO

import pandas as pd
import requests
from django.db import transaction

from .models import Distribuidora, Tarifa


def processar_tarifas_csv(file):
    """
    Processa um arquivo CSV contendo tarifas elétricas, otimizando para grandes arquivos.
    """
    # Ler o CSV
    try:
        df = pd.read_csv(file, delimiter=',', encoding='utf-8')
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo CSV: {str(e)}")

    # Função para conversão segura de valores decimais
    def safe_decimal(value, column_name, index):
        try:
            value = str(value).replace(',', '.').strip()
            if not value or value in ['.', ',', '']:
                return Decimal('0.00')
            return Decimal(value)
        except (InvalidOperation, ValueError) as e:
            raise Exception(f"Erro ao converter '{value}' na coluna '{column_name}' (Linha {index + 1}): {e}")

    # Processar por blocos para lidar com arquivos grandes
    block_size = 10000
    total_rows = len(df)
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
                            'estado': str(row.get('SigAgenteAcessante', ''))[:2]  # Limitar a 2 caracteres
                        }
                    )

                    # Verificar se a tarifa já existe
                    exists = Tarifa.objects.filter(
                        distribuidora=distribuidora,
                        data_inicio_vigencia=pd.to_datetime(row['DatInicioVigencia']),
                        modalidade=row['DscModalidadeTarifaria'],
                        subgrupo=row['DscSubGrupo'],
                        tipo_tarifa=row['DscBaseTarifaria']
                    ).exists()

                    if not exists:
                        # Inserir nova tarifa
                        Tarifa.objects.create(
                            distribuidora=distribuidora,
                            data_inicio_vigencia=pd.to_datetime(row['DatInicioVigencia']),
                            data_fim_vigencia=pd.to_datetime(row['DatFimVigencia']) if pd.notna(row['DatFimVigencia']) else None,
                            modalidade=row['DscModalidadeTarifaria'],
                            subgrupo=row['DscSubGrupo'],
                            tipo_tarifa=row['DscBaseTarifaria'],
                            valor_tusd=safe_decimal(row['VlrTUSD'], 'VlrTUSD', index),
                            valor_te=safe_decimal(row['VlrTE'], 'VlrTE', index),
                            dsc_reh=row.get('DscREH'),
                            dsc_classe=row.get('DscClasse'),
                            dsc_subclasse=row.get('DscSubClasse'),
                            dsc_detalhe=row.get('DscDetalhe'),
                            nom_posto_tarifario=row.get('NomPostoTarifario'),
                            dsc_unidade_terciaria=row.get('DscUnidadeTerciaria')
                        )
                except Exception as e:
                    # Registrar erro
                    erros.append(f"Erro na linha {index + 1}: {e}")
                    continue  # Ignorar linha problemática

    # Retornar status final
    if erros:
        return {"status": "concluído com erros", "detalhes": erros[:10]}  # Limitar erros exibidos
    return {"status": "concluído"}


def processar_tarifas_api(base_url, resource_id):
    """
    Processa tarifas obtidas via API pública da ANEEL com paginação e limite de registros.
    """
    try:
        params = {
            'resource_id': resource_id,
            'limit': 100000,  # Limite por página
            'offset': 0
        }

        erros = []
        while True:
            # Requisição à API
            response = requests.get(base_url, params=params)
            if response.status_code != 200:
                raise Exception(f"Erro na requisição à API: {response.status_code}")

            # Extrair resultados
            data = response.json()
            records = data.get('result', {}).get('records', [])
            if not records:
                break  # Fim dos registros

            # Converter para DataFrame e processar
            df = pd.DataFrame(records)
            resultado = processar_tarifas_csv(StringIO(df.to_csv(index=False)))

            # Coletar erros, se houver
            if resultado['status'] == 'concluído com erros':
                erros.extend(resultado['detalhes'])

            # Avançar para próxima página
            params['offset'] += 100000

        # Retornar resultado
        if erros:
            return {"status": "concluído com erros", "detalhes": erros[:10]}
        return {"status": "concluído"}
    except Exception as e:
        raise Exception(f"Erro ao processar dados da API: {e}")

