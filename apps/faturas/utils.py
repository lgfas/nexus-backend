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


def extract_itens_fatura(pdf_path):
    try:
        # Detecta a codificação do arquivo
        encoding = detect_encoding(pdf_path)

        # Extrai as tabelas do PDF
        tabelas = read_pdf(pdf_path, pages=1, multiple_tables=True, pandas_options={'header': None}, encoding=encoding)

        # Seleciona a tabela relevante
        tabela_itens = tabelas[2]  # Ajustar índice conforme necessário

        # Preprocessamento da tabela
        tabela_itens = tabela_itens.drop([0, 1]).reset_index(drop=True)
        tabela_itens = tabela_itens.iloc[:, :7]
        tabela_itens.columns = [
            "Itens de Fatura", "Quant.", "Preço Unit.(R$)", "Tarifa", "PIS/", "ICMS", "Valor(R$)"
        ]
        tabela_itens = tabela_itens.dropna(subset=["Itens de Fatura"]).reset_index(drop=True)

        # Processamento dos dados
        dados = []
        for _, row in tabela_itens.iterrows():
            valores = str(row["Itens de Fatura"]).split()
            item = " ".join(valores[:-1])
            quant = limpar_numero(valores[-1]) if len(valores) > 1 else None
            dados.append({
                "descricao": item,
                "quantidade": quant,
                "preco_unitario": limpar_numero(row["Quant."]),
                "tarifa": limpar_numero(row["Preço Unit.(R$)"]),
                "pis_cofins": limpar_numero(row["Tarifa"]),
                "icms": limpar_numero(row["PIS/"]),
                "valor": limpar_numero(row["ICMS"]),
            })
        return dados

    except Exception as e:
        raise ValueError(f"Erro ao extrair itens de fatura: {e}")


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


def extract_tributos(pdf_path):
    try:
        # Detecta a codificação do arquivo
        encoding = detect_encoding(pdf_path)

        # Ler tabelas do PDF na página 1
        tabelas = read_pdf(pdf_path, pages=1, multiple_tables=True, pandas_options={'header': None}, encoding=encoding)

        tabela_tributos = tabelas[2]
        tabela_tributos = tabela_tributos.drop(columns=[0, 1, 2, 3, 4, 5, 8, 9])

        tabela_tributos = tabela_tributos.iloc[2:5]
        tabela_tributos.columns = ["Tributo", "Base e Aliquota", "Valor(R$)"]

        tabela_tributos[['Base(R$)', 'Aliquota(%)']] = tabela_tributos['Base e Aliquota'].str.split(' ', n=1, expand=True)
        tabela_tributos = tabela_tributos.drop(columns=["Base e Aliquota"])

        tributos = []
        for _, row in tabela_tributos.iterrows():
            tributos.append({
                "tipo": row["Tributo"].strip(),
                "base": limpar_numero(row['Base(R$)']),
                "aliquota": limpar_numero(row['Aliquota(%)']),
                "valor": limpar_numero(row['Valor(R$)'])
            })
        return tributos

    except Exception as e:
        raise ValueError(f"Erro ao extrair tributos: {e}")

def calcular_tarifa_verde(consumo_ponta, consumo_fora_ponta, tarifa_verde, tributos=0):
    custo_energia = (consumo_ponta + consumo_fora_ponta) * (tarifa_verde.valor_te + tarifa_verde.valor_tusd)
    custo_total = custo_energia + tributos
    return custo_total

def calcular_tarifa_azul(consumo_ponta, consumo_fora_ponta, demanda_ponta, demanda_fora_ponta, tarifa_azul, tributos=0):
    custo_energia = (consumo_ponta * tarifa_azul.valor_te) + (consumo_fora_ponta * tarifa_azul.valor_tusd)
    custo_demanda = (demanda_ponta + demanda_fora_ponta) * tarifa_azul.valor_tusd
    custo_total = custo_energia + custo_demanda + tributos
    return custo_total


def comparar_tarifas(consumo, demanda, tarifas, tributos):
    custo_verde = calcular_tarifa_verde(
        consumo_ponta=consumo["ponta"],
        consumo_fora_ponta=consumo["fora_ponta"],
        tarifa_verde=tarifas["verde"],
        tributos=tributos
    )
    custo_azul = calcular_tarifa_azul(
        consumo_ponta=consumo["ponta"],
        consumo_fora_ponta=consumo["fora_ponta"],
        demanda_ponta=demanda["ponta"],
        demanda_fora_ponta=demanda["fora_ponta"],
        tarifa_ponta=tarifas["azul"]["energia_ponta"],
        tarifa_fora_ponta=tarifas["azul"]["energia_fora_ponta"],
        tarifa_demanda_ponta=tarifas["azul"]["demanda_ponta"],
        tarifa_demanda_fora_ponta=tarifas["azul"]["demanda_fora_ponta"],
        tributos=tributos
    )
    return {
        "melhor_opcao": "Verde" if custo_verde < custo_azul else "Azul",
        "custo_verde": custo_verde,
        "custo_azul": custo_azul
    }
