## Regra de negócio Implementadas

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


