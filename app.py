"""
Dashboard de Validação e Relatórios - Inspeção de Lotes
=========================================================
Interface web (Streamlit) que executa o mesmo pipeline de validação
(RN01, RN02, RN04) usado no script de linha de comando e apresenta
os resultados de forma visual e interativa.

Como executar:
    streamlit run app.py

Requisitos:
    - O módulo `src/validacao.py` deve estar acessível no PYTHONPATH
    (rode o comando a partir da raiz do projeto).
"""

import io
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from src.validacao import (
    validar_estrutura_rn01,
    validar_campos_obrigatorios_rn02,
    verificar_status_rn04,
)

# --------------------------------------------------------------------------- #
# Configuração da página e logging
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Validação de Lotes - Dashboard",
    page_icon="📋",
    layout="wide",
)

LOG_PATH = Path("logs_bot.log")
logging.basicConfig(
    level=logging.INFO,
    filename=str(LOG_PATH),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("dashboard")

CAMINHO_PADRAO = Path("data/samples/inspecao_lotes_dia_teste.xlsx")
CABECALHO_PADRAO = 2


# --------------------------------------------------------------------------- #
# Funções do pipeline (mesma lógica do script original)
# --------------------------------------------------------------------------- #
def abrir_arquivo(origem, cabecalho: int) -> pd.DataFrame:
    """Abre o arquivo Excel a partir de um caminho ou de um upload em memória."""
    return pd.read_excel(io=origem, header=cabecalho)


def aplicar_validacao_status(df: pd.DataFrame) -> list[dict]:
    """
    Aplica a regra RN04 linha a linha.
    Retorna uma lista de erros encontrados (em vez de interromper),
    para que o dashboard possa mostrar todos os problemas de uma vez.
    """
    erros = []
    for index, valor in df["status"].items():
        try:
            df.at[index, "status"] = verificar_status_rn04(valor)
        except ValueError as erro_status:
            msg = f"Linha {index}: {erro_status}"
            logger.error(msg)
            erros.append({"linha": index, "valor_original": valor, "erro": str(erro_status)})
    return erros


def executar_pipeline(df: pd.DataFrame) -> dict:
    """
    Executa RN01 -> RN02 -> RN04 e agrega o resultado em um dicionário
    consumido diretamente pela interface.
    """
    resultado = {
        "rn01_ok": False,
        "rn01_erro": None,
        "rn02_ok": False,
        "rn02_erro": None,
        "rn04_erros": [],
        "df_final": None,
        "sucesso": False,
    }

    # RN01 - Estrutura
    try:
        validar_estrutura_rn01(list(df.columns), logging)
        resultado["rn01_ok"] = True
    except Exception as e:
        resultado["rn01_erro"] = str(e)
        logger.error(f"RN01 falhou: {e}")
        return resultado  # sem estrutura correta, não faz sentido seguir

    # RN02 - Campos obrigatórios
    try:
        validar_campos_obrigatorios_rn02(df, logging)
        resultado["rn02_ok"] = True
    except Exception as e:
        resultado["rn02_erro"] = str(e)
        logger.error(f"RN02 falhou: {e}")
        return resultado

    # RN04 - Status (coleta todos os erros, não para no primeiro)
    resultado["rn04_erros"] = aplicar_validacao_status(df)
    resultado["df_final"] = df
    resultado["sucesso"] = len(resultado["rn04_erros"]) == 0

    if resultado["sucesso"]:
        logger.info("Pipeline de validação concluído com sucesso.")

    return resultado


# --------------------------------------------------------------------------- #
# Estado da sessão
# --------------------------------------------------------------------------- #
if "resultado" not in st.session_state:
    st.session_state.resultado = None
if "nome_arquivo" not in st.session_state:
    st.session_state.nome_arquivo = None


# --------------------------------------------------------------------------- #
# Barra lateral - entrada de dados
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.header("Configuração")

    fonte = st.radio(
        "Fonte do arquivo",
        ["Enviar arquivo (upload)", "Usar caminho padrão do projeto"],
        index=0,
    )

    cabecalho = st.number_input(
        "Linha do cabeçalho (0-indexado)",
        min_value=0,
        max_value=20,
        value=CABECALHO_PADRAO,
        help="Mesmo parâmetro 'header' usado no pd.read_excel do script original.",
    )

    arquivo_upload = None
    if fonte == "Enviar arquivo (upload)":
        arquivo_upload = st.file_uploader("Arquivo .xlsx", type=["xlsx"])
    else:
        st.caption(f"Caminho: `{CAMINHO_PADRAO}`")

    st.divider()
    executar = st.button("Rodar validação", type="primary", use_container_width=True)

    st.divider()
    st.caption(
        "Este dashboard reutiliza as mesmas regras (RN01, RN02, RN04) do "
        "módulo `src.validacao` usado no pipeline em lote."
    )


# --------------------------------------------------------------------------- #
# Execução do pipeline ao clicar no botão
# --------------------------------------------------------------------------- #
if executar:
    try:
        if fonte == "Enviar arquivo (upload)":
            if arquivo_upload is None:
                st.sidebar.error("Selecione um arquivo .xlsx antes de rodar.")
                st.stop()
            df = abrir_arquivo(arquivo_upload, cabecalho)
            st.session_state.nome_arquivo = arquivo_upload.name
        else:
            if not CAMINHO_PADRAO.exists():
                st.sidebar.error(f"Arquivo não encontrado: {CAMINHO_PADRAO}")
                st.stop()
            df = abrir_arquivo(CAMINHO_PADRAO, cabecalho)
            st.session_state.nome_arquivo = str(CAMINHO_PADRAO)

        with st.spinner("Executando validações RN01, RN02 e RN04..."):
            st.session_state.resultado = executar_pipeline(df)

    except Exception as e:
        st.sidebar.error(f"Erro ao abrir/processar o arquivo: {e}")
        st.session_state.resultado = None


# --------------------------------------------------------------------------- #
# Corpo principal
# --------------------------------------------------------------------------- #
st.title("📋 Dashboard de Validação de Lotes")
st.caption("Relatório interativo do pipeline de validação (RN01 · RN02 · RN04)")

resultado = st.session_state.resultado

if resultado is None:
    st.info("Configure a fonte do arquivo na barra lateral e clique em **Rodar validação**.")
else:
    nome = st.session_state.nome_arquivo
    st.markdown(f"**Arquivo analisado:** `{nome}`  \n**Executado em:** {datetime.now():%d/%m/%Y %H:%M:%S}")

    # ---- Métricas gerais -------------------------------------------------
    total_linhas = len(resultado["df_final"]) if resultado["df_final"] is not None else 0
    total_erros_status = len(resultado["rn04_erros"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("RN01 - Estrutura", "OK" if resultado["rn01_ok"] else "Falhou")
    col2.metric("RN02 - Campos obrigatórios", "OK" if resultado["rn02_ok"] else "Falhou")
    col3.metric("RN04 - Linhas com erro de status", total_erros_status)
    col4.metric("Total de linhas processadas", total_linhas)

    st.divider()

    # ---- RN01 --------------------------------------------------------
    if not resultado["rn01_ok"]:
        st.error(f"**RN01 - Estrutura inválida:** {resultado['rn01_erro']}")
        st.stop()

    # ---- RN02 --------------------------------------------------------
    if not resultado["rn02_ok"]:
        st.error(f"**RN02 - Campos obrigatórios ausentes:** {resultado['rn02_erro']}")
        st.stop()

    # ---- RN04 --------------------------------------------------------
    tab_resumo, tab_erros, tab_dados, tab_logs = st.tabs(
        ["Resumo", "Erros (RN04)", "Dados", "Logs"]
    )

    with tab_resumo:
        if resultado["sucesso"]:
            st.success("Pipeline concluído com sucesso — nenhum erro de status encontrado.")
        else:
            st.warning(
                f"Pipeline concluído com **{total_erros_status}** erro(s) de status. "
                "Veja a aba 'Erros (RN04)' para detalhes."
            )

        if resultado["df_final"] is not None and "status" in resultado["df_final"].columns:
            distrib = resultado["df_final"]["status"].value_counts()
            st.subheader("Distribuição de status normalizados")
            st.bar_chart(distrib)

    with tab_erros:
        if total_erros_status == 0:
            st.success("Nenhum erro de validação de status encontrado.")
        else:
            st.dataframe(
                pd.DataFrame(resultado["rn04_erros"]),
                use_container_width=True,
                hide_index=True,
            )

    with tab_dados:
        st.subheader("Dados após validação/normalização")
        st.dataframe(resultado["df_final"], use_container_width=True)

        buffer = io.BytesIO()
        resultado["df_final"].to_excel(buffer, index=False)
        st.download_button(
            "⬇Baixar dados processados (.xlsx)",
            data=buffer.getvalue(),
            file_name="dados_validados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    with tab_logs:
        st.subheader("Últimas linhas de logs_bot.log")
        if LOG_PATH.exists():
            linhas = LOG_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
            st.code("\n".join(linhas[-100:]) or "(log vazio)", language="text")
        else:
            st.info("Arquivo de log ainda não foi criado.")