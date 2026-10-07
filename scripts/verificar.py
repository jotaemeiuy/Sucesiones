import asyncio, sys
from playwright.async_api import async_playwright

# Contra el preview local por defecto; contra producción: verificar.py <url>
BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:4321"
PAGINAS = [
    "/",
    "/capitulo-1/",
    "/capitulo-2/",
    "/capitulo-3/",
    "/capitulo-4/",
    "/formulas/",
    "/practico-sucesiones/",
]
VIEWPORTS = [(360, 800), (768, 1024), (1280, 900)]


async def main():
    fallos = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(viewport={"width": 360, "height": 800})
        page = await ctx.new_page()
        errores = []
        page.on("console", lambda m: errores.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errores.append(str(e)))

        for w, h in VIEWPORTS:
            await page.set_viewport_size({"width": w, "height": h})
            for ruta in PAGINAS:
                await page.goto(BASE + ruta, wait_until="networkidle")
                sw = await page.evaluate("document.documentElement.scrollWidth")
                iw = await page.evaluate("window.innerWidth")
                if sw > iw + 1:
                    fallos.append(f"SCROLL HORIZONTAL {ruta} @{w}px: scrollWidth={sw} innerWidth={iw}")
                print(f"{'OK ' if sw <= iw + 1 else 'FAIL'} {ruta:16} @{w:4}px scrollWidth={sw}")

        # --- calculadoras ---
        await page.set_viewport_size({"width": 1280, "height": 900})
        await page.goto(BASE + "/formulas/", wait_until="networkidle")

        pruebas = [
            ("arit", "despejar a₁ d=5 an=58 → n", {"a1": "3", "d": "5", "n": "", "an": "58"}, "12"),
            ("geom", "Sₙ a₁=3 q=2 n=6", {"a1": "3", "q": "2", "n": "6", "an": ""}, "189"),
            ("fib", "12 términos", {"n": "12"}, "376"),
            ("rec", "a₁=2 r=2 s=-3", {"a1": "2", "r": "2", "s": "-3", "k": "10"}, "-509"),
        ]
        for calc, desc, campos, esperado in pruebas:
            form = page.locator(f'form[data-calc="{calc}"]')
            for nombre, valor in campos.items():
                await form.locator(f'input[name="{nombre}"]').fill(valor)
            await form.locator('button[type="submit"]').click()
            salida = (await form.locator("output").inner_text()).strip()
            ok = esperado in salida
            if not ok:
                fallos.append(f"CALC {calc}: esperaba '{esperado}' en: {salida}")
            print(f"{'OK ' if ok else 'FAIL'} calc {calc:5} {desc:32} → {salida[:110]}")

        # svg del gráfico de recurrencia
        svg = await page.locator('form[data-calc="rec"] [data-chart] svg circle').count()
        if svg != 10:
            fallos.append(f"gráfico recurrencia: {svg} puntos (esperados 10)")
        print(f"{'OK ' if svg == 10 else 'FAIL'} gráfico recurrencia: {svg} puntos")

        # reveal de solución
        await page.goto(BASE + "/capitulo-3/", wait_until="networkidle")
        btn = page.locator("button[data-reveal]").first
        await btn.click()
        sol = await page.locator("button[data-reveal]").first.locator("xpath=../following-sibling::output").inner_text()
        ok = "a > b" in sol or "mayor" in sol
        print(f"{'OK ' if ok else 'FAIL'} RevealSolucion → {sol[:80]}")
        if not ok:
            fallos.append("RevealSolucion sin texto")

        # reveal enriquecido del práctico (panel con KaTeX + aria-expanded)
        await page.goto(BASE + "/practico-sucesiones/", wait_until="networkidle")
        btn = page.locator("#e116 button[data-reveal]")
        await btn.click()
        oculto = await page.locator("#e116-sol").is_hidden()
        katex = await page.locator("#e116-sol .katex").count()
        expandido = await btn.get_attribute("aria-expanded")
        ok = (not oculto) and katex > 0 and expandido == "true"
        print(f"{'OK ' if ok else 'FAIL'} reveal práctico: panel visible, {katex} fórmulas, aria={expandido}")
        if not ok:
            fallos.append(f"reveal práctico: oculto={oculto} katex={katex} aria={expandido}")

        # soluciones del práctico: todos los botones existen (97-126 + 3 preguntas)
        total = await page.locator("button[data-reveal]").count()
        ok = total >= 33
        print(f"{'OK ' if ok else 'FAIL'} práctico: {total} botones de solución (esperados 33)")
        if not ok:
            fallos.append(f"práctico: solo {total} botones de solución")

        if errores:
            fallos.extend("CONSOLA: " + e for e in errores)
        await browser.close()

    print("\n" + ("TODO OK" if not fallos else "FALLOS:"))
    for f in fallos:
        print(" -", f)
    sys.exit(1 if fallos else 0)


asyncio.run(main())
