import asyncio
from playwright.async_api import async_playwright, Response
from typing import List, Dict

MRV_TARGET_URL = "https://ri.mrv.com.br/informacoes-financeiras/central-de-resultados/"
MRV_API_URL = "https://apicatalog.mziq.com/filemanager/company/4b56353d-d5d9-435f-bf63-dcbf0a6c25d5/filter/categories/year/meta"
MRV_INTERNAL_NAME = "central_de_resultados_previa"

CURY_TARGET_URL = "https://ri.cury.net/informacoes-aos-investidores/central-de-resultados/"
CURY_API_URL = "https://apicatalog.mziq.com/filemanager/company/702b9586-4f10-4a79-a7e6-232ce8803136/filter/categories/year/meta"
CURY_INTERNAL_NAME = "previa_operacional"

PLANO_TARGET_URL = "https://ri.planoeplano.com.br/informacoes-financeiras/central-de-resultados/"
PLANO_API_URL = "https://apicatalog.mziq.com/filemanager/company/dd0335cb-6079-40d0-95fc-fbcb3fa580ef/filter/categories/year/meta"
PLANO_INTERNAL_NAME = "central_de_resultados_previa"

DIRECIONAL_TARGET_URL = "https://ri.direcional.com.br/informacoes-financeiras/central-de-resultados/"
DIRECIONAL_API_URL = "https://apicatalog.mziq.com/filemanager/company/ada9bc2c-f7d0-4359-9eaf-851b679ab788/filter/categories/year/meta"
DIRECIONAL_INTERNAL_NAME = "central_de_resultados_previa_operacional"

PACAEMBU_TARGET_URL = "https://ri.pacaembu.com/informacoes-financeiras/central-de-resultados/"
PACAEMBU_API_URL = "https://apicatalog.mziq.com/filemanager/company/e7eb7558-1a9a-4262-b6a6-1167e239272e/filter/categories/year/meta"
PACAEMBU_INTERNAL_NAME = "previa-operacional"

TENDA_TARGET_URL = "https://ri.tenda.com/informacoes-financeiras/central-de-resultados"


async def scrape_select_based(
    context, nome_empresa: str, target_url: str, api_url: str, internal_name: str
) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    page = await context.new_page()
    await page.goto(target_url, wait_until="networkidle")

    try:
        options = await page.locator('#fano option').evaluate_all("opts => opts.map(o => o.value)")
    except Exception:
        options = []

    for value in reversed(options):
        try:
            async with page.expect_response(
                lambda r, _url=api_url: (
                    _url in r.url
                    and r.request.method == "POST"
                ),
                timeout=10000
            ) as response_info:
                await page.select_option("#fano", value)

            response = await response_info.value
            body = await response.json()

            document_metas = body["data"].get("document_metas", [])
            matches = [
                m for m in document_metas
                if internal_name in m.get("internal_name", "")
            ]

            for match in matches:
                url = match.get("file_url", "")
                if url:
                    results.append({
                        "nome_empresa": nome_empresa,
                        "url": url,
                        "trimestre_ano": f"{match.get('file_quarter')}/{match.get('file_year')}",
                    })
        except Exception:
            pass

    await page.close()
    return results


async def main() -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(MRV_TARGET_URL, wait_until="networkidle")

        owl_items = await page.query_selector_all(".owl-stage .owl-item")
        total = len(owl_items)

        for i in range(total - 1, -1, -1):
            api_response_data = None

            async def handle_response(response: Response):
                nonlocal api_response_data
                if MRV_API_URL in response.url:
                    try:
                        body = await response.json()
                        if body.get("success") and "data" in body:
                            api_response_data = body
                    except Exception:
                        pass

            page.on("response", handle_response)

            items = await page.query_selector_all(".owl-stage .owl-item")
            await items[i].click()

            await page.wait_for_timeout(3000)

            page.remove_listener("response", handle_response)

            if api_response_data:
                document_metas = api_response_data["data"].get("document_metas", [])
                matches = [m for m in document_metas if m.get("internal_name") == MRV_INTERNAL_NAME]
                for match in matches:
                    url = match.get("file_url", "")
                    if url:
                        results.append({
                            "nome_empresa": "MRV",
                            "url": url,
                            "trimestre_ano": f"{match.get('file_quarter')}/{match.get('file_year')}",
                        })

        results.extend(
            await scrape_select_based(context, "Cury", CURY_TARGET_URL, CURY_API_URL, CURY_INTERNAL_NAME)
        )

        tenda_page = await context.new_page()
        await tenda_page.goto(TENDA_TARGET_URL, wait_until="networkidle")

        try:
            btn = await tenda_page.query_selector('li > button')
            if btn:
                await btn.click()
        except Exception:
            pass

        try:
            year_elements = await tenda_page.query_selector_all('ul[role="menu"] li a')
            years = []
            for el in year_elements:
                try:
                    label = await el.query_selector('.MuiButton-label')
                    text = await label.inner_text()
                    years.append(text.strip())
                except Exception:
                    pass
        except Exception:
            years = []

        for year in years:
            json_url = (
                f"https://ri.tenda.com/_next/data/ohCbVXmsNsAtyT0pjRhAA/pt"
                f"/informacoes-financeiras/central-de-resultados/{year}.json"
                f"?slug=informacoes-financeiras&slug=central-de-resultados&slug={year}"
            )
            try:
                resp = await tenda_page.request.get(json_url)
                if resp.ok:
                    data = await resp.json()
                    columns = (
                        data.get("pageProps", {})
                        .get("layout", {})
                        .get("page", {})
                        .get("content", {})
                        .get("columns", [])
                    )
                    for column in columns:
                        column_label = column.get("columnLabel", "")
                        posts = column.get("posts", {})
                        found_url = None
                        for post_id, post in posts.items():
                            slug = post.get("postSlug", "")
                            if slug.startswith((
                                "previa-operacional",
                                "previa-dos-resultados-operacionais",
                                "comunicado-ao-mercado",
                            )):
                                found_url = post.get("postUrl")
                                break
                        if found_url and column_label:
                            try:
                                quarter = int(column_label[0])
                                full_year = 2000 + int(column_label[2:])
                                results.append({
                                    "nome_empresa": "Tenda",
                                    "url": found_url,
                                    "trimestre_ano": f"{quarter}/{full_year}",
                                })
                            except (ValueError, IndexError):
                                pass
            except Exception:
                pass

        await tenda_page.close()

        results.extend(
            await scrape_select_based(context, "Plano & Plano", PLANO_TARGET_URL, PLANO_API_URL, PLANO_INTERNAL_NAME)
        )

        results.extend(
            await scrape_select_based(context, "Direcional", DIRECIONAL_TARGET_URL, DIRECIONAL_API_URL, DIRECIONAL_INTERNAL_NAME)
        )

        results.extend(
            await scrape_select_based(context, "Pacaembu", PACAEMBU_TARGET_URL, PACAEMBU_API_URL, PACAEMBU_INTERNAL_NAME)
        )

        await browser.close()

    return results


if __name__ == "__main__":
    data = asyncio.run(main())
    for item in data:
        print(item)
