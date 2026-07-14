import pandas as pd
from pathlib import Path
import logging

# Assumindo que verificar_status foi alocada no módulo src.validacao
from src.validacao import (
    validar_estrutura_rn01, 
    validar_campos_obrigatorios_rn02,
    verificar_status_rn04 
)

CAMINHO_ARQUIVO = Path("data/samples/inspecao_lotes_dia_teste.xlsx")

logging.basicConfig(level=logging.INFO, filename="logs_bot.log", format="%(asctime)s - %(levelname)s - %(message)s")

def abrir_arquivo():
    cabecalho = 2
    df = pd.read_excel(io=CAMINHO_ARQUIVO, header=cabecalho)
    return df

def aplicar_validacao_status(df: pd.DataFrame, logger: logging.Logger):
    """
    Aplica a regra de validação e normalização à coluna 'status'.
    Itera sobre a série e atualiza os valores in-place no DataFrame.
    """
    for index, valor in df['status'].items():
        try:
            # O método at[] atualiza o valor na célula específica com o retorno normalizado
            df.at[index, 'status'] = verificar_status_rn04(valor)
        except ValueError as erro_status:
            msg = f"Falha na validação na linha {index}: {erro_status}"
            logger.error(msg)
            raise ValueError(msg)

def main():
    df = abrir_arquivo()

    try:
        # Validar RN01
        validar_estrutura_rn01(list(df.columns), logging)

        # Validar RN02
        validar_campos_obrigatorios_rn02(df, logging)

        # Validar e Normalizar Status
        aplicar_validacao_status(df, logging)
        
        logging.info("Pipeline de validação concluído com sucesso.")

    except Exception as e:
        print(f"Erro apresentado: {e}")

if __name__ == "__main__":
    main()