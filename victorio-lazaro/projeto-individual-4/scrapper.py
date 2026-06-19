import asyncio
import json
from playwright.async_api import async_playwright, Response

TARGET_URL = "https://ri.mrv.com.br/informacoes-financeiras/central-de-resultados/"
API_URL = "https://apicatalog.mziq.com/filemanager/company/4b56353d-d5d9-435f-bf63-dcbf0a6c25d5/filter/categories/year/meta"
INTERNAL_NAME = "central_de_resultados_itr"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(TARGET_URL, wait_until="networkidle")

        owl_items = await page.query_selector_all(".owl-stage .owl-item")
        total = len(owl_items)
        print(f"Found {total} owl-item(s) in owl-stage")

        for i in range(total - 1, -1, -1):
            api_response_data = None

            async def handle_response(response: Response):
                nonlocal api_response_data
                if API_URL in response.url:
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
                matches = [m for m in document_metas if m.get("internal_name") == INTERNAL_NAME]
                if matches:
                    for match in matches:
                        print(f"owl-item index {i}: file_url={match.get('file_url')}, file_year={match.get('file_year')}, file_title={match.get('file_title')}")
                else:
                    print(f"owl-item index {i}: no entry with internal_name='{INTERNAL_NAME}' found")
            else:
                print(f"owl-item index {i}: no API response captured")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
