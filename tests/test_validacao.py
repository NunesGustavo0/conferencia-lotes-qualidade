# Esse modulo tem a responsabilidade de testar as funcionalidade (Regras de negócio) do modulo validação.py

import pytest
from src.validacao import verificar_lote, verificar_observacao_reprovado
import pandas as pd # Necessário para verificar a planilha

# O Caminho da planilha para o teste do funcionamento:
CAMINHO_PLANILHA = 'data/samples/inspecao_lotes_dia_teste.xlsx'



"""
Regras de negócio 3: Verifica se tem algum lote não existente, caso tenha, ele mostrará a divergência
"""
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

def test_verificar_rn03_caminho_feliz_com_excel(base_referencia_excel):
    """
    Testa se a função que aprova um lote que existe na  planilha de teste
    """

    # 1° Argumento: ID do lote que vai ser verificado e 2° argumento é a base que ele vai procurar
    assert verificar_lote("LG-2026-00101", base_referencia_excel)

def test_verificar_rn03_caminho_errado_excel(base_referencia_excel):
    """
    Testa a RN03 jogando um lote que não existe na planilha
    """

    with pytest.raises(ValueError,match="Lote existe"):
        verificar_lote("LG-2026-00101", base_referencia_excel)


"""
Regra de Negócio 7: Se o Status estiver com "REPROVADO" e não tem nenhum valores no campo de observação, será registrado
a divergência
"""

def test_observacao_reprovado_com_justificativa():
    """Caso 1 (Caminho Feliz): Lote REPROVADO com observação preenchida."""
    assert verificar_observacao_reprovado("REPROVADO", "Embalagem danificada") is True

def test_observacao_reprovado_sem_justificativa():
    """Caso 2 (Falha Esperada): Lote REPROVADO com observação em branco."""
    with pytest.raises(ValueError, match="Falta de Justificativa/Observação"):
        verificar_observacao_reprovado("REPROVADO", "")

def test_observacao_aprovado_sem_justificativa():
    """Caso 3 (Exceção da Regra): Lote APROVADO não exige observação."""
    assert verificar_observacao_reprovado("APROVADO", "") is True

def test_observacao_reprovado_nulo():
    """Caso 4 (Segurança Extra): Lote REPROVADO recebendo valor None (nulo) do Pandas."""
    with pytest.raises(ValueError, match="Falta de Justificativa/Observação"):
        verificar_observacao_reprovado("REPROVADO", None)



"""
Utilizando caso de teste de planilha
"""

@pytest.fixture
def df_inspecao_excel():
    """
    Apenas tem responsabilidade em de fazer a consulta e trazer os dados
    """
    try:
        dataframe = pd.read_excel(CAMINHO_PLANILHA,sheet_name= 'Inspecao')
        return dataframe
    except FileNotFoundError:
        pytest.skip(f"Planilha não encontrada, verifique o caminho: {CAMINHO_PLANILHA}")
    except ValueError:
        pytest.skip(f"Não foi encontrado a aba 'Inspecao' da planilha de teste")

def test_rn07_com_dados_testes(df_inspecao_excel):
    """
    Nesta função de teste, será a verificação de validação da regra de negócio 7
    """

    #Itera sobre para cada linha da planilha carregada
    for indice, linha in df_inspecao_excel.iterrows():
        status = linha.get('status')
        observacao = linha.get('observacao')

        # Caso o status seja reprovado, vamos verificar se tem o campo de observação
        if str(status).upper().strip() == "REPROVADO":

            #Está vazio a observação?
            if pd.isna(observacao) or str (observacao).strip() == "":
                with pytest.raises(ValueError, match="Falta de Justificativa/Observação"):
                    verificar_observacao_reprovado(status, observacao)

        else:
            # Confirma que a função aprova
            assert verificar_observacao_reprovado(status, observacao) is True
