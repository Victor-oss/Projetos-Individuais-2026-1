## Projeto

Eu quero que você modifique o código python na pasta atual, scrapper.py, que usa o playwrigth para baixar todos os relatórios mensais no site da MRV. Você deve adicionar a extração dos pdfs da empresa Cury

#### Tarefas
- O playwright deve entrar no site https://ri.cury.net/informacoes-aos-investidores/central-de-resultados/
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

- Cada vez que ele disparar o evento da option, ele deve pegar a response da requisição https://apicatalog.mziq.com/filemanager/company/702b9586-4f10-4a79-a7e6-232ce8803136/filter/categories/year/meta que é feita ao selecionar a option. Se a request for um sucesso, a response deve ter a estrutura '{
"success": true,
"data": {
"document_metas": [
{', dentro de document_metas existem objetos json. Procure pelo objeto dentro de document_metas com o atributo 'internal_name', igual a 'itr_dfp'. EM seguida, para o objeto encontrado, printe no console do programa python file_url, file_year e file_quarter. Faça essa iteração para todos os options
- uma observação importante é que você deve preservar o código já existente no scrapper.py, a única mudança que você deve fazer é printar também file_quarter ao invés de file_title no código já existente

#### Log de iteração

1) **Tarefa 1 — v1:** Ao rodar o código, estou recebendo o erro '/home/victorio/Documents/Projetos-Individuais-2026-1/victorio-lazaro/projeto-individual-4/scrapper.py:60: RuntimeWarning: coroutine 'BrowserContext.new_page' was never awaited
  async with context.new_page() as cury_page:
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
Traceback (most recent call last):
  File "/home/victorio/Documents/Projetos-Individuais-2026-1/victorio-lazaro/projeto-individual-4/scrapper.py", line 109, in <module>
    asyncio.run(main())
  File "/home/victorio/.pyenv/versions/3.12.0/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/home/victorio/.pyenv/versions/3.12.0/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/victorio/.pyenv/versions/3.12.0/lib/python3.12/asyncio/base_events.py", line 664, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/home/victorio/Documents/Projetos-Individuais-2026-1/victorio-lazaro/projeto-individual-4/scrapper.py", line 60, in main
    async with context.new_page() as cury_page:
TypeError: 'coroutine' object does not support the asynchronous context manager protocol'