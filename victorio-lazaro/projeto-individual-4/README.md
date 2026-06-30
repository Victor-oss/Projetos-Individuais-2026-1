# Prévias Operacionais Scraper

Aplicação que coleta automaticamente prévias operacionais de construtoras brasileiras, extrai indicadores via LLM (OpenAI) e disponibiliza os dados através de uma API REST.

## Arquitetura

```
┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│   Scrapper     │──────▶│   FastAPI       │──────▶│  PostgreSQL    │
│  (Playwright)  │       │   (Uvicorn)     │       │                │
└────────────────┘       └────────────────┘       └────────────────┘
                                │
                                ▼
                         ┌────────────────┐
                         │  OpenAI API    │
                         │  (gpt-4o-mini) │
                         └────────────────┘
```

- **Scrapper**: utiliza Playwright para coletar URLs de PDFs de prévias operacionais das empresas MRV, Pacaembu, Plano & Plano, Tenda, Cury e Direcional.
- **FastAPI**: serviço web que executa o job de scraping a cada 10 minutos, processa os PDFs pendentes e expõe endpoints REST.
- **PostgreSQL**: banco de dados para persistência dos registros coletados e indicadores extraídos.
- **OpenAI API**: utilizada para extração estruturada dos dados de lançamentos e vendas dos PDFs via LLM.

## Configuração do `.env`

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
OPENAI_API_KEY=sk-sua-chave-aqui
```

## Subindo os containers

```bash
docker compose up --build -d
```

Isso irá:
1. Subir o banco PostgreSQL na porta 5432.
2. Buildar e subir a API FastAPI na porta 8000.

Para parar os containers:

```bash
docker compose down
```

## Executando a aplicação

Após subir os containers, a aplicação:
- Cria as tabelas automaticamente no startup.
- Executa o scraping imediatamente e depois a cada 10 minutos.
- Processa PDFs pendentes após cada execução do scraper.

A API estará disponível em: `http://localhost:8000`

### Endpoints disponíveis

| Método | Rota       | Descrição                              |
|--------|------------|----------------------------------------|
| GET    | `/health`  | Health check                           |
| POST   | `/scrape`  | Dispara manualmente o job de scraping  |
| GET    | `/balanco` | Consulta indicadores extraídos         |

## Exemplos de chamadas do endpoint `/balanco`

### Consultar lançamentos

```bash
curl "http://localhost:8000/balanco?nome_empresa=MRV&trimestre=2/2025&tipo=LANCAMENTO"
```

### Consultar vendas

```bash
curl "http://localhost:8000/balanco?nome_empresa=Cury&trimestre=1/2025&tipo=VENDA"
```

### Resposta de sucesso (200)

```json
{
  "id": 1,
  "nome_empresa": "MRV",
  "trimestre": "2/2025",
  "tipo": "LANCAMENTO",
  "valor": 12500.0
}
```

### Resposta não encontrado (404)

```json
{
  "detail": "Registro não encontrado"
}
```

### Parâmetros

| Parâmetro      | Valores aceitos                                          |
|----------------|----------------------------------------------------------|
| `nome_empresa` | MRV, Pacaembu, Plano & Plano, Tenda, Cury, Direcional   |
| `trimestre`    | Formato `{1-4}/{ano}` (ex: `2/2025`)                    |
| `tipo`         | LANCAMENTO, VENDA                                        |

## Tabelas do banco de dados

### `scrappings_previas_operacionais`

| Coluna         | Tipo    | Descrição                                      |
|----------------|---------|------------------------------------------------|
| `id`           | SERIAL  | Chave primária                                 |
| `nome_empresa` | TEXT    | Nome da construtora                            |
| `url`          | TEXT    | URL do PDF da prévia operacional               |
| `trimestre`    | TEXT    | Trimestre no formato `{trimestre}/{ano}`        |
| `is_concluido` | BOOLEAN | Indica se o PDF já foi processado pela LLM     |

### `lancamentos_vendas_empresas`

| Coluna         | Tipo         | Descrição                                  |
|----------------|--------------|--------------------------------------------| 
| `id`           | BIGSERIAL    | Chave primária                             |
| `nome_empresa` | VARCHAR(100) | Nome da construtora                        |
| `trimestre`    | VARCHAR(10)  | Trimestre no formato `{trimestre}/{ano}`    |
| `tipo`         | VARCHAR(20)  | Tipo do indicador (LANCAMENTO ou VENDA)    |
| `valor`        | NUMERIC      | Valor extraído do PDF (null se ausente)    |
