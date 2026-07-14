## Regra de negócio Implementadas

### RN01 - Validação de Estrutura (Padrão de Colunas)

* **Idea:** Foi criada uma funcionalidade para atender a regra RN01, que realiza a verificação de conformidade do layout da planilha recebida para garantir que ela possua exatamente os campos esperados pelo sistema.
* **Como funciona:** O sistema extrai o cabeçalho da planilha carregada e realiza uma operação de diferença de conjuntos (`set`) contra uma coleção de colunas de referência (`lote_id`, `produto`, `linha`, `turno`, `status`, `responsavel`, `data`, `observacao`). A verificação ocorre de forma bidirecional, identificando tanto colunas obrigatórias que estão ausentes quanto colunas intrusas (não padronizadas) que foram inseridas.
* **Tratamento:** Se a estrutura diferir da referência, o sistema levanta uma exceção `ValueError` detalhando exatamente quais colunas faltam ou sobram, registra o evento via *logger* como erro crítico e interrompe o processamento do arquivo.

### RN02 - Validação de Campos Obrigatórios (Valores Nulos)

* **Idea:** Foi criada uma funcionalidade para atender a regra RN02, cujo objetivo é assegurar a completude dos dados processados, impedindo a ingestão de registros com informações essenciais em branco.
* **Como funciona:** O sistema aplica uma máscara booleana vetorizada (`isna()`) sobre todo o *DataFrame* para rastrear a presença de valores nulos nativos (`None` ou `NaN`). Quando a máscara retorna verdadeiro, o algoritmo mapeia as coordenadas matriciais para isolar o índice exato da linha e o nome da coluna da ocorrência.
* **Tratamento:** Ao detectar o primeiro campo vazio, o sistema levanta uma exceção `ValueError` contendo as coordenadas exatas da falha (ex: "linha 1, coluna 'produto'"), registra o evento no log de erros e aborta a validação.

### RN03 - Validação de Existência (Cruzamento com base_referência)

* **Idea:** Foi criado uma funcionalidade para atender a regra RN03, que  realiza o cruzamento de dados para garantir 
a integridade dos lotes recebidos na inspeção diária.

* **Como funciona:** O sistema lê a planilha exportada pelo operador e cruza a coluna `lote_id` com a aba `Base_Referencia`
* **Tratamento:** Se o lote informado não existe na base_referencial, o sistema levanta uma exceção **"Lote não existente"**,
que classifica o registro como divergência. Somente tem a responsabilidade de iniciar a leitura a partir de linha correta

#### Rodando em testes de RN03

```python
# Para rodar todos os testes com saída detalhada
pytest test/ -v

# Rodar apenas os testes que falharam na última execução
pytest --last-failed
```

### RN07 -  Condição de Campo de Observação
Garante que todo o lote recusado pela produção possua uma justificativa rasterável.

* **Ação:** O Sistema avalia se a coluna `status` de cada registro esteja REPROVADO
* **Tratamento:** Caso a coluna `status` seja reprovado, ele verificará se possui o campo de observação, caso não tenha,
registrará como um caso de divergência
* 
## Dependência e Instalação

**Python:** Pode ser utilizado o Python entre 3.11 até 3.14

Biblioteca|Descrição|Versão
:-:|:-:|:-:
Pytest|É um framework de teste para Python que permite desenvolver teste unitários|9.1.1
Pandas|É usado para analisar e manipular dados em tabelas, como se fosse excel|3.0.3
openpyxl|É uma biblioteca que é usada para ler, criar e modificar os arqivos do Excel, não tendo necessidade do software Microsoft Office|3.1.5


