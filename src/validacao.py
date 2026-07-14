import pandas as pd

def verificar_lote(id_lote : str, base_referencia: list):
    """
    Regra de Negócio 3: Validação de existencia
    Verifica se o lote existe na base referência
    """

    if not id_lote or id_lote not in base_referencia:
        raise ValueError(f"""Divergência: Lote não existe\n
                         Lote de id: {id_lote} não foi encontrado na base de referência
                         """)
    return True

def validar_estrutura_rn01(lista: list, logging):
    # Colunas de referencia
    colunas_referencia = {"lote_id", "produto", "linha", "turno", "status", "responsavel", "data", "observacao"}
    # Colunas da planilha recebida
    colunas_recebidas = set(lista)

    colunas_invalidas = colunas_referencia - colunas_recebidas

    if colunas_invalidas:
        msg = f"Falha na RN01: Identificou-se {colunas_invalidas} fora do padrão estipulado"
        logging.error(msg)
        raise ValueError(msg)
    
def validar_campos_obrigatorios_rn02(df, logger):
    # Cria uma máscara booleana onde True representa valores nulos
    mascara_nulos = df.isna()
    
    if mascara_nulos.any().any():
        # Extrai as coordenadas exatas (índice da linha e nome da coluna) onde há True na máscara
        coordenadas = mascara_nulos[mascara_nulos].stack().index.tolist()
        
        # Formata o primeiro erro
        primeiro_erro = coordenadas[0]
        linha_erro, coluna_erro = primeiro_erro
        
        msg = f"Falha na RN02: Valor ausente ou nulo encontrado na linha {linha_erro}, coluna '{coluna_erro}'."
        logger.error(msg)
        raise ValueError(msg)