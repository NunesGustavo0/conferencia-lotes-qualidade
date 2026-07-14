# Esse modulo tem responsabilidade de ter  as regras de negócio

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
    status_normalizado = str(status).strip().upper if status else ""

    if status_normalizado == 'REPROVADO':
    #Verificcando se o campo de observação está vazia
        if not (observacao or str(observacao).strip() == "" or str(observacao).lower() == 'nan'):
            raise ValueError("Divergência: Falta de Justificativa no campo de observação em lote em REPROVADO")
    return True

