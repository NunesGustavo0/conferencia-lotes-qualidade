import pandas as pd
import logging

def verificar_lote(id_lote : str, base_referencia: list) -> bool:
    """
    Regra de Negócio 3: Validação de existencia
    Verifica se o lote existe na base referência
    """

    if not id_lote or id_lote not in base_referencia:
        raise ValueError(f"""Divergência: Lote não existe\n
                         Lote de id: {id_lote} não foi encontrado na base de referência
                         """)
    return True

def verificar_observacao_reprovado(status : str, observacao: str):
    """
    Regra de Negócio 7: Condição de Observação
    Verifica SE o status for igual a "REPROVADO" e o campo de observação estiver vazia
    ENTÃO registrar a linha como divergência por "Falta de Justificativa/Observação"
    """

    #Vamos padronizar o texto para evitar erros de CamelSensitive
    status_normalizado = str(status).strip().upper() if status else ""

    if status_normalizado == 'REPROVADO':
    #Verificcando se o campo de observação está vazia
        if not (observacao or str(observacao).strip() == "" or str(observacao).lower() == 'nan'):
            raise ValueError("Divergência: Falta de Justificativa no campo de observação em lote em REPROVADO")
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
    
def normalizar_status_rn05(status: str) -> str:
    """
    Normaliza os status específicos 'OK' e 'NOK' para o padrão do sistema.
    """
    mapeamento = {
        "OK": "APROVADO",
        "NOK": "REPROVADO"
    }
    # Retorna o valor mapeado; se não existir no dicionário, retorna o próprio status
    return mapeamento.get(status, status)

def verificar_status_rn04(status: str, logging) -> str:
    """
    Verifica se o status pertence ao escopo de regras de negócio.
    Aciona a normalização caso identifique entradas 'OK' ou 'NOK'.
    """
    # Tratamento defensivo da entrada
    status_tratado = str(status).strip().upper()

    # Validação e acionamento da normalização
    if status_tratado in {"OK", "NOK"}:
        status_tratado = normalizar_status_rn05(status_tratado)

    # Conjunto de referência (Operação O(1))
    status_permitidos = {"APROVADO", "REPROVADO", "PENDENTE"}

    if status_tratado not in status_permitidos:
        msg = f"Erro de validação: Status '{status}' não reconhecido."
        logging.error(msg)
        raise ValueError(msg)

    return status_tratado