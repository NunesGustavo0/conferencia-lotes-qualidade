# Esse modulo tem a responsabilidade de testar as funcionalidade (Regras de negócio) do modulo validação.py

import pytest
from src.validacao import verificar_lote
import pandas as pd # Necessário para verificar a planilha

# O Caminho da planilha para o teste do funcionamento:
CAMINHO_PLANILHA = 'data/samples/inspecao_lotes_dia_teste.xlsx'


@pytest.fixture
def base_referencia_excel():
    """
    Essa função é responsável por lê a aba "Base_Referencia" do Excel, que retorna uma lista
    de lotes válidos para ser usada nos testes
    """

    try:
        df_base_referencia = pd.read_excel(CAMINHO_PLANILHA,
                                           sheet_name = "Base_Referencia",
                                           header = 1
                                           )

        #Conversão de dataframe para lista (Pegando somente o lote_id)
        lista_lotes = (df_base_referencia['lote_id']
                       .dropna()
                       .astype(str)
                       .to_list())

        return lista_lotes
    except FileNotFoundError:
        pytest.skip(f"Planilha não encontrada, por favor, verifique se o caminho está correto: {CAMINHO_PLANILHA}")

def test_verificar_caminho_feliz_com_excel(base_referencia_excel):
    """
    Testa se a função que aprova um lote que existe na  planilha de teste
    """

    # 1° Argumento: ID do lote que vai ser verificado e 2° argumento é a base que ele vai procurar
    assert verificar_lote("LG-2026-00101", base_referencia_excel)

def test_verificar_caminho_errado_excel(base_referencia_excel):
    """
    Testa a RN03 jogando um lote que não existe na planilha
    """

    with pytest.raises(ValueError,match="Lote existe"):
        verificar_lote("LG-2026-00101", base_referencia_excel)