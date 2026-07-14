import pandas as pd
from pathlib import Path
import logging
from src.validacao import validar_estrutura_rn01, validar_campos_obrigatorios_rn02

CAMINHO_ARQUIVO = Path("data/samples/inspecao_lotes_dia_teste.xlsx")

logging.basicConfig(level=logging.INFO, filename="logs_bot.log", format="%(asctime)s - %(levelname)s - %(message)s")

def abrir_arquivo():
    cabecalho = 2
    df = pd.read_excel(io=CAMINHO_ARQUIVO, header=cabecalho)
    return df

def main():
    df = abrir_arquivo()

    try:
        # Validar RN01
        validar_estrutura_rn01(list(df.columns), logging)

        # Validar RN02
        validar_campos_obrigatorios_rn02(df, logging)

    except Exception as e:
        print(f"Erro apresentado: {e}")

if __name__ == "__main__":
    main()