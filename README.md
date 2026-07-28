# Conferência de Lotes - Qualidade

Bot de validação e conferência de lotes de qualidade, com geração automática de relatórios de divergências e dashboard web para acompanhamento.

## Regras de Negócio Implementadas

### RN01 - Validação de Estrutura (Padrão de Colunas)

**Ideia:** Funcionalidade que realiza a verificação de conformidade do layout das planilhas recebidas, garantindo que possuam exatamente os campos esperados pelo sistema.

**Como funciona:** O sistema extrai o cabeçalho da planilha e realiza uma operação de diferença de conjuntos (`set`) contra uma coleção de colunas de referência (`lote_id`, `produto`, `linha`, `turno`, `status`, `responsavel`, `data`, `observacao`). A verificação ocorre de forma bidirecional, identificando tanto colunas obrigatórias ausentes quanto colunas intrusas (não padronizadas) que foram inseridas.

**Tratamento:** Se a estrutura difere da referência, o sistema levanta uma exceção `ValueError` detalhando quais colunas faltam ou sobram, registra o evento via logger como erro crítico e interrompe o processamento do arquivo.

### RN02 - Validação de Campos Obrigatórios (Valores Nulos)

**Ideia:** Funcionalidade que garante a integridade dos dados processados, impedindo a entrada de registros com informações essenciais em branco.

**Como funciona:** O sistema aplica uma máscara booleana vetorizada (`isna()`) sobre todo o DataFrame para rastrear a presença de valores nulos nativos (`None` ou `NaN`). Quando a máscara retorna verdadeira, o algoritmo mapeia as coordenadas matriciais para isolar o índice exato da linha e o nome da coluna da ocorrência.

**Tratamento:** Ao detectar o primeiro campo vazio, o sistema levanta uma exceção `ValueError` contendo as coordenadas exatas da falha (ex.: "linha 1, coluna 'produto'"), registra o evento no log de erros e aborta a validação.

### RN03 - Validação de Existência (Cruzamento com base_referência)

**Ideia:** Funcionalidade que realiza cruzamentos de dados para garantir a integridade dos lotes recebidos nas fiscalizações diárias.

**Como funciona:** O sistema lê a planilha exportada pelo operador e cruza a coluna `lote_id` com a aba `Base_Referencia`.

**Tratamento:** Se o lote informado não existe na base de referência, o sistema levanta uma exceção de "Lote não existente", classificando o registro como divergência.

### RN04 - Validação e Normalização de Status

**Ideia:** Funcionalidade que garante que o status do lote esteja contido no domínio de valores permitidos e padronizados pelo sistema.

**Como funciona:** O algoritmo intercepta o valor da coluna de status de cada registro, realiza uma limpeza de formatação (remoção de espaços em branco e conversão para minúsculas) e aplica uma normalização preliminar (mapeando "OK" para "APROVADO" e "NOK" para "REPROVADO"). Após a normalização, o valor é validado contra um conjunto de referência de escopo fechado (`{"APROVADO", "REPROVADO", "PENDENTE"}`), utilizando busca em complexidade de tempo O(1).

**Tratamento:** Se o status recebido não for reconhecido e não puder ser normalizado, o sistema levanta uma exceção `ValueError` detalhando o erro e a linha correspondente, efetua o registro no log e interrompe o pipeline de processamento.

### RN05 - *[Nome da Validação - Necessita Definição]*

**Ideia:** *(Inserir o objetivo de negócio da regra. Exemplo: assegurar a unicidade dos registros, impedindo a ingestão de lotes duplicados no mesmo turno.)*

**Como funciona:** *(Inserir a mecânica da regra. Exemplo: o sistema aplica o método `.duplicated()` sobre a coluna `lote_id`, retornando uma máscara booleana para mapear colisões de dados na planilha atual.)*

**Tratamento:** *(Inserir o comportamento de falha. Exemplo: ao identificar a duplicidade, o sistema levanta uma exceção `ValueError` referente às linhas conflitantes e aborta o processamento.)*

### RN07 - Condição de Campo de Observação

**Ideia:** Garantir que todo lote recusado pela produção possua uma justificativa rastreável.

**Ação:** O sistema avalia se a coluna `status` de cada registro está `REPROVADO`.

**Tratamento:** Caso o status seja `REPROVADO`, o sistema verifica se o campo de observação foi preenchido; caso não tenha, registra como um caso de divergência.

### Geração de Relatórios
O bot consolida todas as divergências encontradas durante a validação das regras de negócio (Lotes Inexistentes, 
Status divergentes, Falta de Observação, etc.) e exporta automaticamente um arquivo `.xlsx` estruturado, seguindo o 
padrão da seção 12 do PDD.

### Geração de Relatórios
O bot consolida todas as divergências encontradas durante a validação das regras de negócio (Lotes Inexistentes, 
Status divergentes, Falta de Observação, etc.) e exporta automaticamente um arquivo `.xlsx` estruturado, seguindo o 
padrão da seção 12 do PDD.

#### Rodando testes

## Geração de Relatórios

O bot consolida todas as divergências ocorridas durante a validação das regras de negócio (lotes inexistentes, status divergentes, falta de observação, etc.) e exporta automaticamente um arquivo `.xlsx` estruturado, seguindo o padrão da seção 12 do PDD.

## Dashboard Web (Interface de Relatórios)

Além da execução em lote (`bot.py`), o projeto conta com um dashboard interativo (`app.py`), construído em Streamlit, para visualização dos relatórios de validação (RN01, RN02 e RN04) direto no navegador — com upload de planilha, métricas de resumo, tabela de erros e exportação dos dados processados.

Para rodar:

```bash
pip install streamlit
streamlit run app.py
```

## Rodando os testes

```bash
# Para rodar todos os testes com saída detalhada
pytest test/ -v

# Rodar apenas os testes que falharam na última execução
pytest --last-failed
```

#### Rodando o bot

```bash
#Para rodar o bot, digite seguinte comando:
docker compose up

# para caso você tenha rodado mais uma vez, execute seguinte comando para eliminar o cache: 
docker compose run -rm bot
```


**Python:** pode ser utilizado o Python entre as versões 3.11 e 3.14.

| Biblioteca | Descrição                                                                                   | Versão |
|------------|----------------------------------------------------------------------------------------------|--------|
| Pytest     | Framework de teste para Python que permite desenvolver testes unitários                     | 9.1.1  |
| Pandas     | Usado para analisar e manipular dados em tabelas, como se fosse Excel                       | 3.0.3  |
| openpyxl   | Biblioteca usada para ler, criar e modificar arquivos do Excel, sem necessidade do Office    | 3.1.5  |

Instalação das dependências:

```bash
pip install -r requirements.txt
```