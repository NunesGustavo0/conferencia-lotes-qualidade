import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock

# Ajuste a importação para incluir a função da RN02
from src.validacao import verificar_lote, validar_campos_obrigatorios_rn02, verificar_observacao_reprovado

# O Caminho da planilha para o teste do funcionamento:
CAMINHO_PLANILHA = 'data/samples/inspecao_lotes_dia_teste.xlsx'

# ==========================================
# FIXTURES
# ==========================================


"""
Regras de negócio 3: Verifica se tem algum lote não existente, caso tenha, ele mostrará a divergência
"""
@pytest.fixture
def base_referencia_excel():
    """
    Lê a aba "Base_Referencia" do Excel e retorna uma lista de lotes válidos.
    """
    try:
        df_base_referencia = pd.read_excel(CAMINHO_PLANILHA,
                                           sheet_name="Base_Referencia",
                                           header=1)

        lista_lotes = (df_base_referencia['lote_id']
                       .dropna()
                       .astype(str)
                       .to_list())

        return lista_lotes
    except FileNotFoundError:
        pytest.skip(f"Planilha não encontrada, verifique o caminho: {CAMINHO_PLANILHA}")

@pytest.fixture
def mock_logger():
    """Fixture para injetar um logger simulado e interceptar logs de erro nos testes."""
    return MagicMock()

# ==========================================
# TESTES RN03: Verificação de Lote
# ==========================================

def test_verificar_caminho_feliz_com_excel(base_referencia_excel):
    """Testa a aprovação de um lote que existe na planilha de teste."""
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

def test_verificar_caminho_errado_excel(base_referencia_excel):
    """Testa a RN03 injetando um lote que sabidamente não existe na planilha."""
    # O lote testado deve ser diferente do caminho feliz para acionar a falha
    with pytest.raises(ValueError, match="Lote existe"): 
        verificar_lote("LOTE-INEXISTENTE-999", base_referencia_excel)

# ==========================================
# TESTES RN02: Campos Obrigatórios
# ==========================================

def test_rn02_caso_1_vazio_tipo_none(mock_logger):
    """Testa a identificação de um campo vazio gerado por um objeto nulo nativo (None)."""
    df = pd.DataFrame({
        "lote_id": [101, 102, 103],
        "produto": ["Alpha", None, "Gamma"], 
        "status": ["OK", "OK", "OK"]
    })
    
    with pytest.raises(ValueError, match="linha 1, coluna 'produto'"):
        validar_campos_obrigatorios_rn02(df, mock_logger)
        
    mock_logger.error.assert_called_once()

def test_rn02_caso_2_vazio_tipo_nan(mock_logger):
    """Testa a identificação de um campo vazio gerado por np.nan."""
    df = pd.DataFrame({
        "lote_id": [101, 102, np.nan], 
        "produto": ["Alpha", "Beta", "Gamma"],
        "status": ["OK", "OK", "OK"]
    })
    
    with pytest.raises(ValueError, match="linha 2, coluna 'lote_id'"):
        validar_campos_obrigatorios_rn02(df, mock_logger)

def test_rn02_caso_3_multiplos_vazios_prioridade(mock_logger):
    """Testa se o método identifica e relata corretamente a primeira ocorrência matricial."""
    df = pd.DataFrame({
        "lote_id": [101, np.nan, 103], 
        "produto": [np.nan, "Beta", "Gamma"], 
        "status": ["OK", "OK", "Erro"]
    })
    
    with pytest.raises(ValueError, match="linha 0, coluna 'produto'"):
        validar_campos_obrigatorios_rn02(df, mock_logger)

def test_rn02_caminho_feliz_sem_vazios(mock_logger):
    """Testa a aprovação da validação quando o DataFrame está totalmente preenchido."""
    df = pd.DataFrame({
        "lote_id": [101, 102, 103],
        "produto": ["Alpha", "Beta", "Gamma"],
        "status": ["OK", "OK", "OK"]
    })
    
    try:
        validar_campos_obrigatorios_rn02(df, mock_logger)
    except ValueError:
        pytest.fail("ValueError foi levantado inesperadamente em um DataFrame sem valores nulos.")
    
    mock_logger.error.assert_not_called()