import asyncio
from playwright.async_api import async_playwright

async def capture_screenshots():
    print("🚀 Iniciando motor de capturas (Playwright)...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Tamaño desktop estándar para dashboards
        page = await browser.new_page(viewport={"width": 1366, "height": 768})
        
        async def wait_and_snap(url, path):
            print(f"Navegando a {url} ...")
            await page.goto(url)
            try:
                # 15 segundos para despertar y renderizar todo
                print("Esperando 15s para renderizado de Streamlit...")
                await page.wait_for_timeout(15000) 
                await page.screenshot(path=path)
                print(f"✅ Captura guardada en: {path}")
            except Exception as e:
                print(f"❌ Error capturando {url}: {e}")

        # Capturas base
        await wait_and_snap("https://datamark-analytics.streamlit.app/", "imagen/placeholder_landing.png")
        await wait_and_snap("https://datamark-analytics.streamlit.app/Ingesta_Ventas", "imagen/placeholder_ingesta.png")
        
        # Intento de clic en el Tab del CRUD Paginado
        print("Navegando hacia el Tab de CRUD...")
        try:
            # Los tabs en streamlit suelen usar rol de tab o boton
            await page.get_by_text("Control Base de Datos", exact=True).click()
            print("Clic en tab exitoso. Esperando 5s para renderizado de Data Editor...")
            await page.wait_for_timeout(5000)
            await page.screenshot(path="imagen/placeholder_crud.png")
            print("✅ Captura guardada en: imagen/placeholder_crud.png")
        except Exception as e:
            print(f"⚠️ No se pudo dar click al Tab, tomando fallback: {e}")
            await page.screenshot(path="imagen/placeholder_crud.png") # Fallback

        # Dashboard View
        await wait_and_snap("https://datamark-analytics.streamlit.app/dashboard", "imagen/placeholder_dashboard.png")

        await browser.close()
        print("🎉 Proceso de capturas finalizado.")

if __name__ == "__main__":
    asyncio.run(capture_screenshots())
