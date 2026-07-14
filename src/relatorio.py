# Nesse modulo terá a responsabilidade de gerar relatório final

import pandas as pd
import os
from src.validacao import *


CAMINHO_SAIDA = "data/output/relatorio_divergencias.xlsx"

def gerar_relatorio_divergencias(dados: list, caminho_saida: str) -> bool:
    """
    Gera relatório .xlsx contendo os registros de divergência
    """
    try:
        if not dados:
            df = pd.DataFrame(columns=["lote_id","status","observacao","motivo_divergencia"])
        else:
            df = pd.DataFrame(dados)

        os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

        df.to_excel(caminho_saida,index=False,engine='openpyxl')
        return True

    except Exception as e:
        raise IOError(f"Erro ao gerar relatório: \nMotivo:{e}")


