## Projeto

Eu quero que você modifique o código python na pasta atual, scrapper.py, que usa o playwrigth para baixar todos os relatórios mensais de 4 sites. Você deve adicionar a extração dos pdfs da empresa Direcional

#### Tarefas
- O playwright deve entrar no site https://ri.direcional.com.br/informacoes-financeiras/central-de-resultados/
- Em seguida, o código deve procurar pelo select com id "fano" e clicar em cada uma das options desse select, mas faça na ordem da última até a primeira
- Cada vez que ele disparar o evento da option, ele deve pegar a response da requisição 
https://apicatalog.mziq.com/filemanager/company/ada9bc2c-f7d0-4359-9eaf-851b679ab788/filter/categories/meta que é feita ao selecionar a option. Se a request for um sucesso, a response deve ter a estrutura '{
"success": true,
"data": {
"document_metas": [
{', dentro de document_metas existem objetos json. Procure pelo objeto dentro de document_metas com o atributo 'internal_name', igual a 'central_de_resultados_itrdfp'. EM seguida, para o objeto encontrado, printe no console do programa python file_url, file_year e file_quarter. Faça essa iteração para todos os options
- uma observação importante é que você deve preservar o código já existente no scrapper.py
- uma observação importante é que essa extração é similar Às feitas pela cury e pela plano&plano. Faça então um método para que essas 3 extrações (incluindo a da direcional) chamem o mesmo método, só mudando os parâmetros