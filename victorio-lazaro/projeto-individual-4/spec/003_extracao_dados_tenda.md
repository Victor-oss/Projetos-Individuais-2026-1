## Projeto

Eu quero que você modifique o código python na pasta atual, scrapper.py, que usa o playwrigth para baixar todos os relatórios mensais no site da MRV e da Cury. Você deve adicionar a extração das urls dos pdfs da empresa Tenda

#### Tarefas
- O playwright deve entrar no site https://ri.tenda.com/informacoes-financeiras/central-de-resultados
- Em seguida, o código deve procurar pelo botão '<li><button class="MuiButtonBase-root MuiButton-root MuiButton-text jss147 MuiButton-textPrimary MuiButton-disableElevation" tabindex="0" type="button"><span class="MuiButton-label"><svg class="MuiSvgIcon-root jss148" focusable="false" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 10c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm12 0c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm-6 0c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"></path></svg></span><span class="MuiTouchRipple-root"></span></button></li>' e clicar nele. Ele abre um div parecido com '<div class="MuiPaper-root MuiMenu-paper MuiPopover-paper jss149 MuiPaper-elevation8 MuiPaper-rounded" tabindex="-1" style="opacity: 1; transform: none; transition: opacity 333ms cubic-bezier(0.4, 0, 0.2, 1) 0ms, transform 222ms cubic-bezier(0.4, 0, 0.2, 1) 0ms; top: 37px; left: 348px; transform-origin: 0px 192.5px;"><ul class="MuiList-root MuiMenu-list jss150 MuiList-padding" role="menu" tabindex="-1"><div class="jss151 jss154" tabindex="0"><div class="jss152"><div class="jss155"></div><div class="jss155"></div><li class="jss144"><a class="MuiButtonBase-root MuiButton-root MuiButton-text jss144 MuiButton-textPrimary MuiButton-disableElevation" tabindex="0" aria-disabled="false" href="/informacoes-financeiras/central-de-resultados/2012"><span class="MuiButton-label"><span>2012</span></span><span class="MuiTouchRipple-root"></span></a></li>'. Para cada li no div, você deve pegar o ano dentro do span dentro do span com classe 'MuiButton-label'. Faça uma lista com todos os anos encontrados e do último até o primeiro item da lista, vocÊ deve fazer uma requisição GET parecida com "https://ri.tenda.com/_next/data/ohCbVXmsNsAtyT0pjRhAA/pt/informacoes-financeiras/central-de-resultados/$ANO_ENCONTRADO.json?slug=informacoes-financeiras&slug=central-de-resultados&slug=ANO_ENCONTRADO", usando o ano encontrado.
- A response dessa requisição tem formato json abaixo

```
{
    "pageProps": {
        "layout": {
            "page": {
                "content": {
                    "columns": [
                        {
                            "columnKey": "2023-03-31T03:00:00.000Z",
                            "columnLabel": "1T23",
                            "isActive": true,
                            "posts": {
                                "0555e6df-92e3-4fd0-b233-50262c6acc77": {
                                    "postUuid": "83a6d64f-23ac-4a9b-8183-8a3505ce5238",
                                    "postShortId": "kmrbmn",
                                    "postType": "file",
                                    "postLanguage": "pt",
                                    "postTitle": "Release de Resultados",
                                    "postSlug": "release-de-resultados",
                                    "postUrl": "https://media.sumaq.report/tenda-1d6b229e/docs/Press-release-Tenda-2023-03-31-Rhbbgk6j.pdf",
                                    "referenceDate": "2023-03-31T03:00:00.000Z",
                                    "deliveryDate": "2023-05-04T14:01:41.927Z",
                                    "fileMimeType": "application/pdf",
                                    "fileSize": 2111225,
                                    "openInNewWindow": true,
                                    "documentTypeUuid": "8c548b22-9ee1-4b32-b15f-7c6c11460a60",
                                    "documentTypeName": "Press-release",
                                    "documentTypeShortName": null
                                },
```
- para cada objeto dentro de columns, você deve imprimir o ano encontrado, o columnLabel e o atributo postUrl para o primeiro objeto dentro de posts que possui postSlug igual a "itr" ou postSlug igual a "dfp"
