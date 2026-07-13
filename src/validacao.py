# Esse modulo tem responsabilidade de ter  as regras de negócio

def verificar_lote(id_lote : str, base_referencia: list):
    """
    Regra de Negócio 3: Validação de existencia
    Verifica se o lote existe na base referência
    """

    if not id_lote or id_lote not in base_referencia:
        raise ValueError(f"""Divergência: Lote não existe\n
                         Lote de id: {id_lote} não foi encontrado na base de referência
                         """)
