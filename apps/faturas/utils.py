import re
from datetime import datetime
import tabula
import pandas as pd

def limpar_numero(valor):
    """
    Remove pontos de milhar e substitui vírgulas por pontos nos números.
    Exemplo: '6.426,00' -> 6426.00
    """
    try:
        return float(str(valor).replace('.', '').replace(',', '.'))
    except ValueError:
        return None

def extract_fatura_data(pdf_path):
    """
    Extrai os dados gerais da fatura, incluindo informações de ContaEnergia e ItensFatura.
    """
    data = {
        "mes": None,
        "vencimento": None,
        "total_pagar": None,
        "leitura_anterior": None,
        "leitura_atual": None,
        "numero_dias": None,
        "proxima_leitura": None,
        "demanda_contratada": None,
        "itens_fatura": []
    }

    try:
        # Ler tabelas do PDF
        tabelas = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True, encoding="utf-8")

        # Processar dados gerais
        for tabela in tabelas:
            for _, row in tabela.iterrows():
                if pd.isnull(row.iloc[0]):
                    continue  # Ignorar linhas vazias

                linha = str(row.iloc[0]).upper()
                if "VENCIMENTO" in linha:
                    data["mes"] = datetime.strptime(f"01/{row.iloc[0]}", "%d/%m/%Y")
                    data["vencimento"] = datetime.strptime(row.iloc[1], "%d/%m/%Y")
                elif "TOTAL A PAGAR" in linha:
                    data["total_pagar"] = limpar_numero(row.iloc[2])
                elif "LEITURA ANTERIOR" in linha:
                    data["leitura_anterior"] = limpar_numero(row.iloc[1])
                    data["leitura_atual"] = limpar_numero(row.iloc[2])
                    data["numero_dias"] = int(row.iloc[3]) if row.iloc[3].isdigit() else None
                    data["proxima_leitura"] = datetime.strptime(row.iloc[4], "%d/%m/%Y")
                elif "DEMANDA CONTRATADA" in linha:
                    data["demanda_contratada"] = limpar_numero(row.iloc[1])

        # Processar tabela de itens
        tabela_itens = tabelas[2]  # Supondo que a tabela de itens é a terceira tabela
        for _, row in tabela_itens.iterrows():
            try:
                data["itens_fatura"].append({
                    "consumo_ponta": limpar_numero(row.iloc[1]),
                    "consumo_fora_ponta": limpar_numero(row.iloc[2]),
                    "demanda_ativa": limpar_numero(row.iloc[3]),
                    "adicional_bandeira": limpar_numero(row.iloc[4])
                })
            except (IndexError, ValueError):
                continue  # Ignorar linhas inválidas

    except Exception as e:
        print(f"Erro ao processar fatura: {e}")

    return data

def extract_historico_data(pdf_path):
    """
    Extrai a tabela de histórico de consumo e demanda a partir do PDF.
    """
    historico = []

    try:
        # Ler tabelas do PDF
        tabelas = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True, encoding="utf-8")
        tabela_historico = tabelas[-1]  # Supondo que a tabela de histórico é a última

        for _, row in tabela_historico.iterrows():
            try:
                partes = str(row.iloc[0]).split()
                if len(partes) >= 4:  # Garantir que há dados suficientes na linha
                    mes_abrev = partes[0][:3].upper()
                    if mes_abrev in MESES_PORTUGUES:
                        historico.append({
                            "mes": datetime(year=2024, month=MESES_PORTUGUES[mes_abrev], day=1),
                            "demanda_medida_ponta": limpar_numero(partes[1]),
                            "demanda_medida_fora_ponta": limpar_numero(partes[2]),
                            "demanda_medida_reativo_excedente": limpar_numero(partes[3]),
                            "consumo_faturado_ponta_tot": limpar_numero(partes[4]),
                            "consumo_faturado_fora_ponta": limpar_numero(partes[5]),
                            "consumo_faturado_reativo_excedente": limpar_numero(partes[6]),
                            "horario_reservado_consumo": limpar_numero(partes[7]),
                            "horario_reservado_reativo_excedente": limpar_numero(partes[8]),
                        })
            except (IndexError, ValueError):
                continue  # Ignorar linhas inválidas

    except Exception as e:
        print(f"Erro ao processar histórico: {e}")

    return historico


# Dicionário de meses abreviados para números
MESES_PORTUGUES = {
    "JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4, "MAI": 5, "JUN": 6,
    "JUL": 7, "AGO": 8, "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12
}
