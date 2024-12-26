import pandas as pd
from tabula import read_pdf

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

def extract_itens_fatura(pdf_path):
    try:
        tabelas = read_pdf(pdf_path, pages=1, multiple_tables=True, pandas_options={'header': None})
        tabela_itens = tabelas[2]  # Ajustar índice conforme necessário

        tabela_itens = tabela_itens.drop([0, 1]).reset_index(drop=True)
        tabela_itens = tabela_itens.iloc[:, :7]
        tabela_itens.columns = [
            "Itens de Fatura", "Quant.", "Preço Unit.(R$)", "Tarifa", "PIS/", "ICMS", "Valor(R$)"
        ]
        tabela_itens = tabela_itens.dropna(subset=["Itens de Fatura"]).reset_index(drop=True)

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
        # Ler as tabelas do PDF na página 2
        tabelas = read_pdf(pdf_path, pages=2, multiple_tables=True, pandas_options={'header': None})

        # Selecionar a tabela correta (primeira tabela)
        tabela_historico = tabelas[0]

        # Remover linhas vazias e redefinir índice
        tabela_historico = tabela_historico.dropna(how='all').reset_index(drop=True)

        # Definir nomes das colunas (com distinções para colunas repetidas)
        colunas = [
            "MÊS",
            "demanda_medida_ponta",
            "demanda_medida_fora_ponta",
            "demanda_medida_reativo_excedente",
            "consumo_faturado_ponta_tot",
            "consumo_faturado_fora_ponta",
            "consumo_faturado_reativo_excedente",
            "horario_reservado_consumo",
            "horario_reservado_reativo_excedente"
        ]

        # Processar os valores das linhas
        dados = []
        for _, row in tabela_historico.iloc[3:16].iterrows():  # Ignorar as primeiras três linhas
            # Combinar os valores das colunas dividindo-os corretamente
            valores = (
                row[0].split() +  # Mês e demanda
                row[2].split() +  # Consumo faturado
                row[3].split()    # Horário reservado
            )

            # Validar quantidade de valores
            if len(valores) >= len(colunas):
                linha = dict(zip(colunas, valores[:len(colunas)]))

                # Converter 'MÊS' para número inteiro (1-12)
                linha['MÊS'] = mes_para_numero(linha['MÊS'])

                # Converter os valores para o formato esperado (float)
                dados.append({
                    "mes": linha["MÊS"],
                    "demanda_medida_ponta": limpar_numero(linha["demanda_medida_ponta"]),
                    "demanda_medida_fora_ponta": limpar_numero(linha["demanda_medida_fora_ponta"]),
                    "demanda_medida_reativo_excedente": limpar_numero(linha["demanda_medida_reativo_excedente"]),
                    "consumo_faturado_ponta_tot": limpar_numero(linha["consumo_faturado_ponta_tot"]),
                    "consumo_faturado_fora_ponta": limpar_numero(linha["consumo_faturado_fora_ponta"]),
                    "consumo_faturado_reativo_excedente": limpar_numero(linha["consumo_faturado_reativo_excedente"]),
                    "horario_reservado_consumo": limpar_numero(linha["horario_reservado_consumo"]),
                    "horario_reservado_reativo_excedente": limpar_numero(linha["horario_reservado_reativo_excedente"]),
                })

        return dados

    except Exception as e:
        raise ValueError(f"Erro ao extrair histórico: {e}")


def extract_tributos(pdf_path):
    try:
        # Ler tabelas do PDF na página 1
        tabelas = read_pdf(pdf_path, pages=1, multiple_tables=True, pandas_options={'header': None})

        # Selecionar a tabela relevante (ajustar índice se necessário)
        tabela_tributos = tabelas[2]

        # Remover colunas indesejadas
        tabela_tributos = tabela_tributos.drop(columns=[0, 1, 2, 3, 4, 5, 8, 9])

        # Manter apenas as linhas relevantes (ICMS, PIS e COFINS)
        tabela_tributos = tabela_tributos.iloc[2:5]

        # Renomear colunas
        tabela_tributos.columns = ["Tributo", "Base e Aliquota", "Valor(R$)"]

        # Separar colunas combinadas
        tabela_tributos[['Base(R$)', 'Aliquota(%)']] = tabela_tributos['Base e Aliquota'].str.split(' ', n=1, expand=True)

        # Remover coluna combinada antiga
        tabela_tributos = tabela_tributos.drop(columns=["Base e Aliquota"])

        # Processar e retornar os tributos
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


