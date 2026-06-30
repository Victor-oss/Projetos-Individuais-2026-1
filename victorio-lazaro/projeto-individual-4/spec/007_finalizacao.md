## Projeto

Estou desenvolvendo uma aplicação composta por:

* Um serviço FastAPI.
* Um banco PostgreSQL.
* Um docker-compose responsável por subir ambos os containers.

A aplicação executa um job a cada 10 minutos que chama o script `scrapper.py`.

O script retorna uma lista onde cada item possui os seguintes campos:

* `nome_empresa` (MRV, Pacaembu, Plano & Plano, Tenda, Cury ou Direcional)
* `url`
* `trimestre` no formato `{trimestre}/{ano}` (exemplo: `2/2025`)

Existe uma tabela PostgreSQL chamada `scrappings_previas_operacionais` contendo:

* `id`
* `nome_empresa`
* `url`
* `trimestre`

Ao final da execução do scraper:

1. Todos os registros da tabela `scrappings_previas_operacionais` são carregados.
2. É criado um conjunto (`set`) contendo todas as URLs já cadastradas.
3. Para cada item retornado pelo scraper:

   * Se a URL já existir, ignorar.
   * Se a URL não existir, inserir um novo registro.

## Tarefas

### 1. Controle de processamento

Adicionar à tabela `scrappings_previas_operacionais` uma coluna:

```sql
is_concluido BOOLEAN
```

Após o término do job de coleta das URLs:

1. Buscar todos os registros cujo `is_concluido` seja `false` ou `NULL`.
2. Para cada registro encontrado:

   * Fazer download do PDF da URL.
   * Extrair o conteúdo utilizando PyMuPDF.
   * Realizar uma estratégia de chunking semântico do conteúdo extraído.
   * Enviar apenas os trechos relevantes para a API da OpenAI utilizando a chave presente no arquivo `.env`.

### 2. Extração estruturada via LLM

A resposta do LLM deve obrigatoriamente seguir um contrato semântico validado com Pydantic.

O schema esperado é:

```python
class BalancoOperacional(BaseModel):
    total_lancamentos: float | None
    total_vendas: float | None
```

Regras:

* O modelo não deve inventar valores.
* Caso uma informação não esteja presente no PDF, retornar `null`.
* O retorno deve conter apenas dados encontrados explicitamente no documento.
* O resultado deve ser validado via Pydantic antes de ser persistido.

### 3. Persistência dos indicadores

Criar uma tabela chamada:

```sql
lancamentos_vendas_empresas
```

com as colunas:

```sql
id BIGSERIAL PRIMARY KEY,
nome_empresa VARCHAR(100),
trimestre VARCHAR(10),
tipo VARCHAR(20),
valor NUMERIC
```

Para cada PDF processado:

* Inserir um registro com:

  * `tipo = 'LANCAMENTO'`
  * `valor = total_lancamentos`

* Inserir outro registro com:

  * `tipo = 'VENDA'`
  * `valor = total_vendas`

Após o processamento com sucesso:

```sql
is_concluido = true
```

na tabela `scrappings_previas_operacionais`.

### 4. Endpoint REST

Criar o endpoint:

```http
GET /balanco
```

Parâmetros obrigatórios:

#### nome_empresa

Aceitar apenas:

* MRV
* Pacaembu
* Plano & Plano
* Tenda
* Cury
* Direcional

#### trimestre

Validar o formato:

```text
{trimestre}/{ano}
```

Exemplos válidos:

```text
1/2025
2/2025
3/2025
4/2025
```

Regras:

* trimestre entre 1 e 4
* ano com exatamente 4 dígitos

#### tipo

Aceitar apenas:

* LANCAMENTO
* VENDA

### Comportamento do endpoint

Retornar o registro com maior ID que possua:

* mesmo nome_empresa
* mesmo trimestre
* mesmo tipo

Caso nenhum registro seja encontrado:

Retornar HTTP 404.

### 5. README

Adicionar um README na raiz do projeto contendo:

* descrição da arquitetura
* instruções para configuração do arquivo `.env`
* instruções para subir os containers com Docker Compose
* instruções para executar a aplicação
* exemplos de chamadas do endpoint `/balanco`
* descrição das tabelas criadas
