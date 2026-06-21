## Projeto

Eu quero que você modifique o código python na pasta atual, scrapper.py, que usa o playwrigth para baixar todos os relatórios mensais no site da MRV, Cury e Tenda. Você deve adicionar a extração dos pdfs da empresa Plano & Plano

#### Tarefas
- O playwright deve entrar no site https://ri.planoeplano.com.br/informacoes-financeiras/central-de-resultados/
- Em seguida, o código deve procurar pelo select com id "fano" e clicar em cada uma das options desse select, como no código abaixo, mas faça na ordem da última até a primeira

```
const options = await page.locator('#fano option').evaluateAll(options =>
    options.map(option => option.value)
);

for (const value of options) {
    await page.selectOption('#fano', value);

    await page.waitForLoadState('networkidle');
}
```

- Cada vez que ele disparar o evento da option, ele deve pegar a response da requisição 
https://apicatalog.mziq.com/filemanager/company/dd0335cb-6079-40d0-95fc-fbcb3fa580ef/filter/categories/year/meta que é feita ao selecionar a option. Se a request for um sucesso, a response deve ter a estrutura '{
"success": true,
"data": {
"document_metas": [
{', dentro de document_metas existem objetos json. Procure pelo objeto dentro de document_metas com o atributo 'internal_name', igual a 'central_de_resultados_itr'. EM seguida, para o objeto encontrado, printe no console do programa python file_url, file_year e file_quarter. Faça essa iteração para todos os options
- uma observação importante é que você deve preservar o código já existente no scrapper.py
