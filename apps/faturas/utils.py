from datetime import datetime

def extract_fatura_data(reader):
    """
    Extrai os dados gerais da fatura, incluindo ContaEnergia e ItensFatura.
    """
    data = {
        "cliente_id": 1,  # ID do cliente (substitua conforme necessário)
        "mes": datetime.strptime("2024-09-01", "%Y-%m-%d"),  # Exemplo de mês de consumo
        "vencimento": datetime.strptime("2024-09-30", "%Y-%m-%d"),  # Data de vencimento
        "total_pagar": 1500.75,  # Total a pagar extraído do PDF
        "leitura_anterior": 5000.00,  # Exemplo de leitura anterior
        "leitura_atual": 5200.00,  # Exemplo de leitura atual
        "numero_dias": 30,  # Número de dias no ciclo
        "proxima_leitura": datetime.strptime("2024-10-31", "%Y-%m-%d"),  # Data da próxima leitura
        "demanda_contratada": 300.0,  # Exemplo de demanda contratada
        "itens_fatura": []  # Preenchido a seguir
    }

    # Extração de itens da fatura
    for page in reader.pages:
        text = page.extract_text()

        if "Itens de Fatura" in text:
            lines = text.splitlines()
            for line in lines:
                if "Consumo Ponta" in line:
                    data["itens_fatura"].append({
                        "consumo_ponta": 6426.00,
                        "consumo_fora_ponta": 5000.00,
                        "demanda_ativa": 23940.27,
                        # Adicione os demais campos de ItensFatura conforme necessário
                        "adicional_bandeira": 15.00,  # Exemplo
                    })

    return data



# Dicionário para meses em português
MESES_PORTUGUES = {
    "JAN": 1,
    "FEV": 2,
    "MAR": 3,
    "ABR": 4,
    "MAI": 5,
    "JUN": 6,
    "JUL": 7,
    "AGO": 8,
    "SET": 9,
    "OUT": 10,
    "NOV": 11,
    "DEZ": 12,
}

def extract_historico_data(reader):
    """
    Extrai a tabela de histórico de consumo e demanda.
    """
    historico = []
    for page in reader.pages:
        text = page.extract_text()

        if "Histórico dos últimos meses" in text:
            lines = text.splitlines()
            for line in lines:
                # Verificar se a linha começa com uma abreviação de mês em português
                mes_abrev = line[:3].upper()  # Pega os 3 primeiros caracteres da linha
                if mes_abrev in MESES_PORTUGUES:
                    parts = line.split()  # Divide a linha em partes
                    mes_num = MESES_PORTUGUES[mes_abrev]

                    # Substituir vírgulas por pontos antes da conversão para float
                    try:
                        historico.append({
                            "cliente_id": 1,  # ID do cliente associado
                            "mes": datetime(year=2024, month=mes_num, day=1),  # Definindo o dia como 1º do mês
                            "demanda_medida_ponta": float(parts[1].replace(',', '.')),
                            "demanda_medida_fora_ponta": float(parts[2].replace(',', '.')),
                            "demanda_medida_reativo_excedente": float(parts[3].replace(',', '.')),
                            "consumo_faturado_ponta_tot": float(parts[4].replace(',', '.')),
                            "consumo_faturado_fora_ponta": float(parts[5].replace(',', '.')),
                            "consumo_faturado_reativo_excedente": float(parts[6].replace(',', '.')),
                            "horario_reservado_consumo": float(parts[7].replace(',', '.')),
                            "horario_reservado_reativo_excedente": float(parts[8].replace(',', '.')),
                        })
                    except ValueError as e:
                        print(f"Erro ao processar linha: {line} -> {e}")
                        continue

    return historico

