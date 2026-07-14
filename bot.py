import pandas as pd
from pathlib import Path
import logging
from src.relatorio import gerar_relatorio_divergencias, CAMINHO_SAIDA

# Assumindo que verificar_status foi alocada no módulo src.validacao
from src.validacao import *

CAMINHO_ARQUIVO = Path("data/samples/inspecao_lotes_dia_teste.xlsx")

logging.basicConfig(level=logging.INFO, filename="logs_bot.log", format="%(asctime)s - %(levelname)s - %(message)s")


def abrir_arquivo():
    cabecalho = 2
    df = pd.read_excel(io=CAMINHO_ARQUIVO, header=cabecalho, sheet_name="Inspecao")
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    # Remove linhas de rodapé/legenda (ex: "Total de registros...", "LEGENDA...", "Exemplo")
    # que não são lotes de inspeção reais.
    linhas_invalidas = df['lote_id'].astype(str).str.contains(
        r'^(Total de registros|LEGENDA|Exemplo)', case=False, na=False
    )
    df = df[~linhas_invalidas].reset_index(drop=True)

    return df

def obter_base_referencia():
    """Lê a aba de referência para aplicar a RN03."""
    try:
        df_base = pd.read_excel(io=CAMINHO_ARQUIVO, sheet_name="Base_Referencia", header=1)
        return df_base['lote_id'].dropna().astype(str).tolist()
    except Exception as e:
        logging.error(f"Erro ao carregar base de referência: {e}")
        return []

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

def aplicar_validacoes_por_linha(df: pd.DataFrame, base_referencia: list, logger: logging.Logger, divergencias: list):
    """
    Itera sobre as linhas do DataFrame aplicando as regras específicas (RN03, RN04, RN07).
    """
    for index, linha in df.iterrows():
        lote_id = linha.get('lote_id')
        status = linha.get('status')
        observacao = linha.get('observacao')

        # RN03: Validação de Existência na Base
        try:
            verificar_lote(lote_id, base_referencia)
        except ValueError as erro_rn03:
            logger.warning(f"Linha {index} - Lote {lote_id}: Falha RN03")
            divergencias.append({
                "lote_id": str(lote_id),
                "status": str(status),
                "observacao": str(observacao) if pd.notna(observacao) else "",
                "motivo_divergencia": str(erro_rn03).strip()
            })

        # RN04 e RN05: Validação e Normalização de Status
        try:
            novo_status = verificar_status_rn04(status, logger)
            df.at[index, 'status'] = novo_status  # Atualiza in-place para as próximas regras
            status = novo_status # Atualiza a variável local
        except ValueError as erro_rn04:
            logger.warning(f"Linha {index} - Lote {lote_id}: Falha RN04")
            divergencias.append({
                "lote_id": str(lote_id),
                "status": str(status),
                "observacao": str(observacao) if pd.notna(observacao) else "",
                "motivo_divergencia": str(erro_rn04).strip()
            })

        # RN07: Validação de Observação para Reprovados
        try:
            verificar_observacao_reprovado(status, observacao)
        except ValueError as erro_rn07:
            logger.warning(f"Linha {index} - Lote {lote_id}: Falha RN07")
            divergencias.append({
                "lote_id": str(lote_id),
                "status": str(status),
                "observacao": str(observacao) if pd.notna(observacao) else "",
                "motivo_divergencia": str(erro_rn07).strip()
            })


def main():
    try:
        logging.info("Carregando bases de dados...")
        df = abrir_arquivo()
        base_referencia = obter_base_referencia()
        lista_divergencias = []

        logging.info("Iniciando pipeline de validação estrutural...")

        # Regras Críticas: Se falharem, o robô levanta exceção e interrompe tudo
        validar_estrutura_rn01(list(df.columns), logging)
        validar_campos_obrigatorios_rn02(df, logging)

        logging.info("Estrutura válida. Iniciando validações linha a linha...")

        # Regras de Negócio: Acumulam erros para o relatório
        aplicar_validacoes_por_linha(df, base_referencia, logging, lista_divergencias)

        # Geração do Relatório de Saída
        if len(lista_divergencias) > 0:
            logging.info(f"Foram encontradas {len(lista_divergencias)} divergências. Gerando relatório...")
            gerar_relatorio_divergencias(lista_divergencias, CAMINHO_SAIDA)
            print(f"⚠️ [{len(lista_divergencias)} divergências encontradas] Relatório salvo em: {CAMINHO_SAIDA}")
        else:
            logging.info("Nenhuma divergência encontrada na base.")
            print("✅ [Sucesso] Inspeção concluída sem divergências! Nenhum relatório gerado.")

    except Exception as e:
        # Pega os erros críticos (RN01 e RN02) ou arquivos não encontrados
        print(f"❌ Erro Crítico que interrompeu a execução: {e}")
        logging.error(f"Execução abortada. Motivo: {e}")


if __name__ == "__main__":
    main()