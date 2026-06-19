## Projeto

Eu quero que você crie um código python na pasta atual, scrapper.py, que usa o playwrigth para baixar todos os relatórios mensais no site da MRV

#### Tarefas
- O playwright deve entrar no site https://ri.mrv.com.br/informacoes-financeiras/central-de-resultados/
- Em seguida, ele deve pegar o html interno da única div com a classe 'owl-stage' na página. Em seguida, ele deve clicar em cada div que está dentro dessa 'owl-stage', as divs com a classe 'owl-item'
- O playwrigth deve clicar em cada uma dessas divs, na ordem da última até a primeira. Cada vez que ele clicar numa div, ele deve pegar a response da requisição https://apicatalog.mziq.com/filemanager/company/4b56353d-d5d9-435f-bf63-dcbf0a6c25d5/filter/categories/year/meta que é feita ao clicar na div. Se a request for um sucesso, a response deve ter a estrutura '{
    "success": true,
    "data": {
        "document_metas": [
            {', dentro de document_metas existem objetos json. Procure pelo objeto dentro de document_metas com o atributo 'internal_name', igual a 'central_de_resultados_itr'. EM seguida, para o objeto encontrado, printe no console do programa python file_url e o file_year. Faça essa iteração para todos os itens de 'owl-stage'

#### Log de iteração

1) **Tarefa 1 — v1:** ficou bom, só sugiro uma modificação, ao invés de pegar só um objeto com central_de_resultados_itr, pegue todos. Além de printar file_url e file_year, printe também file_title