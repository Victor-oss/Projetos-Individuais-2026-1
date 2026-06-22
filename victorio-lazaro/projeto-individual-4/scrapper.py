import asyncio
import json
from playwright.async_api import async_playwright, Response

MRV_TARGET_URL = "https://ri.mrv.com.br/informacoes-financeiras/central-de-resultados/"
MRV_API_URL = "https://apicatalog.mziq.com/filemanager/company/4b56353d-d5d9-435f-bf63-dcbf0a6c25d5/filter/categories/year/meta"
MRV_INTERNAL_NAME = "central_de_resultados_itr"

CURY_TARGET_URL = "https://ri.cury.net/informacoes-aos-investidores/central-de-resultados/"
CURY_API_URL = "https://apicatalog.mziq.com/filemanager/company/702b9586-4f10-4a79-a7e6-232ce8803136/filter/categories/year/meta"
CURY_INTERNAL_NAME = "itr_dfp"

PLANO_TARGET_URL = "https://ri.planoeplano.com.br/informacoes-financeiras/central-de-resultados/"
PLANO_API_URL = "https://apicatalog.mziq.com/filemanager/company/dd0335cb-6079-40d0-95fc-fbcb3fa580ef/filter/categories/year/meta"
PLANO_INTERNAL_NAME = "central_de_resultados_itr"

DIRECIONAL_TARGET_URL = "https://ri.direcional.com.br/informacoes-financeiras/central-de-resultados/"
DIRECIONAL_API_URL = "https://apicatalog.mziq.com/filemanager/company/ada9bc2c-f7d0-4359-9eaf-851b679ab788/filter/categories/year/meta"
DIRECIONAL_INTERNAL_NAME = "central_de_resultados_itrdfp"

PACAEMBU_TARGET_URL = "https://ri.pacaembu.com/informacoes-financeiras/central-de-resultados/"
PACAEMBU_API_URL = "https://apicatalog.mziq.com/filemanager/company/e7eb7558-1a9a-4262-b6a6-1167e239272e/filter/categories/year/meta"
PACAEMBU_INTERNAL_NAME = "ITR_DFP"

TENDA_TARGET_URL = "https://ri.tenda.com/informacoes-financeiras/central-de-resultados"

async def scrape_select_based(context, name, target_url, api_url, internal_name):
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
            matches = [m for m in document_metas if m.get("internal_name") == internal_name]

            if matches:
                for match in matches:
                    print(f"{name} option {value}: file_url={match.get('file_url')}, file_year={match.get('file_year')}, file_quarter={match.get('file_quarter')}")
            else:
                print(f"{name} option {value}: no entry with internal_name='{internal_name}' found")
        except Exception as e:
            print(f"{name} option {value}: {e}")

    await page.close()


async def main():
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
                if matches:
                    for match in matches:
                        print(f"mrv index {i}: file_url={match.get('file_url')}, file_year={match.get('file_year')}, file_quarter={match.get('file_quarter')}")
                else:
                    print(f"mrv index {i}: no entry with internal_name='{MRV_INTERNAL_NAME}' found")
            else:
                print(f"mrv index {i}: no API response captured")

        await scrape_select_based(context, "cury", CURY_TARGET_URL, CURY_API_URL, CURY_INTERNAL_NAME)

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
            json_url = f"https://ri.tenda.com/_next/data/ohCbVXmsNsAtyT0pjRhAA/pt/informacoes-financeiras/central-de-resultados/{year}.json?slug=informacoes-financeiras&slug=central-de-resultados&slug={year}"
            try:
                resp = await tenda_page.request.get(json_url)
                if resp.ok:
                    data = await resp.json()
                    columns = data.get('pageProps', {}).get('layout', {}).get('page', {}).get('content', {}).get('columns', [])
                    for column in columns:
                        column_label = column.get('columnLabel')
                        posts = column.get('posts', {})
                        found_url = None
                        for post_id, post in posts.items():
                            slug = post.get('postSlug')
                            if slug.startswith(('itr', 'dfp')):
                                found_url = post.get('postUrl')
                                break
                        if found_url:
                            print(f"tenda year {year}: columnLabel={column_label}, postUrl={found_url}")
                else:
                    print(f"tenda year {year}: failed to fetch json ({resp.status})")
            except Exception as e:
                print(f"error tenda year {year}: {e}")

        await tenda_page.close()

        await scrape_select_based(context, "plano", PLANO_TARGET_URL, PLANO_API_URL, PLANO_INTERNAL_NAME)

        await scrape_select_based(context, "direcional", DIRECIONAL_TARGET_URL, DIRECIONAL_API_URL, DIRECIONAL_INTERNAL_NAME)

        await scrape_select_based(context, "pacaembu", PACAEMBU_TARGET_URL, PACAEMBU_API_URL, PACAEMBU_INTERNAL_NAME)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
