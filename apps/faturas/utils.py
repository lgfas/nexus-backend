import os
import pandas as pd
from tabula import read_pdf
import chardet
from decimal import Decimal, InvalidOperation


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


def tratar_tabela_itens(tabela, index):
    """
    Ajusta a tabela de itens para garantir que todas as colunas estejam devidamente preenchidas.
    """
    # Remover linhas irrelevantes
    tabela = tabela.drop([0, 1]).reset_index(drop=True)

    # Selecionar apenas as primeiras 7 colunas
    tabela = tabela.iloc[:, :7]
    tabela.columns = [
        "Itens de Fatura", "Quant.", "Preço Unit.(R$)", "Tarifa", "PIS/", "ICMS", "Valor(R$)"
    ]

    # Remover linhas onde "Itens de Fatura" está vazio
    tabela = tabela.dropna(subset=["Itens de Fatura"]).reset_index(drop=True)

    # Ajustar desalinhamentos específicos
    for i, row in tabela.iterrows():
        # Verificar desalinhamento em "Preço Unit.(R$)" e corrigir se necessário
        if pd.isnull(row["Preço Unit.(R$)"]) and not pd.isnull(row["Tarifa"]):
            tabela.loc[i, "Preço Unit.(R$)"] = row["Tarifa"]
            tabela.loc[i, "Tarifa"] = row["PIS/"]
            tabela.loc[i, "PIS/"] = row["ICMS"]
            tabela.loc[i, "ICMS"] = row["Valor(R$)"]
            tabela.loc[i, "Valor(R$)"] = None

    return tabela


def identificar_tabela(tabelas):
    """
    Identifica a tabela correta de itens com base no conteúdo.
    """
    for idx, tabela in enumerate(tabelas):
        # Procurar por indicadores de que a tabela contém itens de fatura
        if any(tabela[0].str.contains("Consumo Ponta", na=False, regex=True)):
            return tabela, idx
    raise ValueError("Tabela de itens de fatura não encontrada no PDF.")


def extract_itens_fatura_generalizado(pdf_path):
    """
    Extrai os itens da fatura de um PDF.
    """
    try:
        # Detecta a codificação do arquivo
        encoding = detect_encoding(pdf_path)

        # Extrai todas as tabelas do PDF
        tabelas = read_pdf(pdf_path, pages=1, multiple_tables=True, pandas_options={'header': None}, encoding=encoding)

        # Identifica a tabela relevante
        tabela_itens, tabela_idx = identificar_tabela(tabelas)

        # Ajusta a tabela identificada
        tabela_itens = tratar_tabela_itens(tabela_itens, tabela_idx)

        # Processar os dados
        dados = []
        for _, row in tabela_itens.iterrows():
            valores = str(row["Itens de Fatura"]).split()
            descricao = " ".join(valores[:-1]) if len(valores) > 1 else row["Itens de Fatura"]
            quantidade = limpar_numero(valores[-1]) if len(valores) > 1 else limpar_numero(row["Quant."])

            dados.append({
                "descricao": descricao,
                "quantidade": quantidade,
                "preco_unitario": limpar_numero(row["Preço Unit.(R$)"]),
                "tarifa": limpar_numero(row["Tarifa"]),
                "pis_cofins": limpar_numero(row["PIS/"]),
                "icms": limpar_numero(row["ICMS"]),
                "valor": limpar_numero(row["Valor(R$)"]),
            })

        return dados

    except Exception as e:
        raise ValueError(f"Erro ao extrair itens de fatura: {e}")
