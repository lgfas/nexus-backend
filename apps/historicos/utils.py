import os
import pandas as pd
from tabula import read_pdf
import chardet

def limpar_numero(valor):
    """
    Remove pontos de milhar e substitui vírgulas por pontos nos números.
    Exemplo: '6.426,00' -> 6426.00
    """
    try:
        # Trata valores 'nan' como None
        if pd.isnull(valor) or str(valor).strip().lower() == 'nan':
            return None
        return float(str(valor).replace('.', '').replace(',', '.'))
    except ValueError:
        return None


def detect_encoding(pdf_path):
    """
    Detecta a codificação do arquivo PDF usando a biblioteca chardet.
    """
    with open(pdf_path, 'rb') as file:
        raw_data = file.read()
    result = chardet.detect(raw_data)
    return result['encoding'] or 'utf-8'  # Usa UTF-8 como fallback

def mes_para_numero(abreviacao):
    """
    Converte abreviações de meses (ex: JAN, FEV) para números (ex: 1, 2).
    """
    meses = {
        "JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4,
        "MAI": 5, "JUN": 6, "JUL": 7, "AGO": 8,
        "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12
    }
    return meses.get(abreviacao.upper())

def extract_historico_data(pdf_path):
    try:
        # Detecta a codificação do arquivo
        encoding = detect_encoding(pdf_path)

        # Ler as tabelas do PDF na página 2
        tabelas = read_pdf(pdf_path, pages=2, multiple_tables=True, pandas_options={'header': None}, encoding=encoding)

        # Selecionar a tabela correta
        tabela_historico = tabelas[0]
        tabela_historico = tabela_historico.dropna(how='all').reset_index(drop=True)

        # Processar valores
        dados = []
        for _, row in tabela_historico.iloc[3:16].iterrows():
            valores = (
                row[0].split() +
                row[2].split() +
                row[3].split()
            )
            if len(valores) >= 9:
                dados.append({
                    "mes": mes_para_numero(valores[0]),
                    "demanda_medida_ponta": limpar_numero(valores[1]),
                    "demanda_medida_fora_ponta": limpar_numero(valores[2]),
                    "demanda_medida_reativo_excedente": limpar_numero(valores[3]),
                    "consumo_faturado_ponta_tot": limpar_numero(valores[4]),
                    "consumo_faturado_fora_ponta": limpar_numero(valores[5]),
                    "consumo_faturado_reativo_excedente": limpar_numero(valores[6]),
                    "horario_reservado_consumo": limpar_numero(valores[7]),
                    "horario_reservado_reativo_excedente": limpar_numero(valores[8]),
                })
        return dados

    except Exception as e:
        raise ValueError(f"Erro ao extrair histórico: {e}")