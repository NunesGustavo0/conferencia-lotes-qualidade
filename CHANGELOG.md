# ChangeLog

Todas as modificações notáveis neste projeto serão documentados
nesse arquivo

O formato baseia-se em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao 
[Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased] (ou [0.1.0] - 2026-07-13)

### Foram adicionados:
- Regras de negócio RN01, RN02 e RN03 integradas ao código principal do bot
- Implementação da RN01 e RN02 no módulo `src/validacao.py`, através da função `validar_estrutura_rn01` e `validar_campos_obrigatorios_rn02` respectivamente.
- Implementação da RN03 no módulo `src/validacao.py`, através da função `verificar_lote` para validação de existência de lotes.
- Suíte de testes unitários com `pytest` no arquivo `tests/test_validacao.py`, abrangendo cenários de caminho feliz, lotes inexistentes, valores nulos e vazios.
- Criação de uma `fixture` no pytest integrada ao `pandas` para ler e injetar os dados da planilha oficial de testes (`inspecao_lotes_teste.xlsx`).
- Configuração do parâmetro `header=1` no `pandas.read_excel` para contornar problemas de layout com o título mesclado na primeira linha do arquivo da LG.
- Código parcialmente integrado a biblioteca logging


### Quais são as dependências
- Inclusão das bibliotecas `pandas` e `openpyxl` para o processamento em lote da base referência contida na aba do Excel
- Inclusão de bibliotecas `logging` para geração de logs de execução