import pandas as pd
from tabula import read_pdf

def limpar_numero(valor):
    """
    Remove pontos de milhar e substitui vírgulas por pontos nos números.
    Exemplo: '6.426,00' -> 6426.00
    """
    try:
        return float(str(valor).replace('.', '').replace(',', '.'))
    except ValueError:
        return None

def extract_itens_fatura(pdf_path):
    """
    Extrai os dados da tabela de itens de fatura do PDF.
    """
    tabelas = read_pdf(pdf_path, pages=1, multiple_tables=True, pandas_options={'header': None})
    tabela_itens = tabelas[2]  # Ajustar índice conforme necessário

    # Remover as duas primeiras linhas irrelevantes
    tabela_itens = tabela_itens.drop([0, 1]).reset_index(drop=True)

    # Selecionar apenas as primeiras 7 colunas relevantes
    tabela_itens = tabela_itens.iloc[:, :7]

    # Renomear as colunas
    tabela_itens.columns = [
        "Itens de Fatura", "Quant.", "Preço Unit.(R$)", "Tarifa", "PIS/", "ICMS", "Valor(R$)"
    ]

    # Limpar valores inconsistentes
    tabela_itens = tabela_itens.dropna(subset=["Itens de Fatura"]).reset_index(drop=True)

    # Processar linhas
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

def extract_historico_data(pdf_path):
    """
    Extrai os dados da tabela de histórico do PDF.
    """
    tabelas = read_pdf(pdf_path, pages=2, multiple_tables=True, pandas_options={'header': None})
    tabela_historico = tabelas[0]  # Ajustar índice conforme necessário

    # Remover linhas vazias e redefinir índice
    tabela_historico = tabela_historico.dropna(how='all').reset_index(drop=True)

    # Definir nomes das colunas corrigidos
    colunas = [
        "MÊS", "PONTA", "FORA PONTA", "REATIVO EXCEDENTE",
        "PONTA/TOT", "FORA PONTA", "REATIVO EXCEDENTE",
        "CONSUMO", "REATIVO EXCEDENTE"
    ]

    # Processar os valores das linhas
    dados = []
    for _, row in tabela_historico.iloc[2:16].iterrows():
        valores = row[0].split() + row[2].split() + row[3].split()
        if len(valores) >= len(colunas):
            dados.append(dict(zip(colunas, valores[:len(colunas)])))

    # Criar DataFrame final
    df = pd.DataFrame(dados)
    df = df[df["MÊS"] != "MÊS"].reset_index(drop=True)
    return df.to_dict(orient="records")
