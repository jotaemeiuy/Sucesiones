# AGENTS.md — Sucesiones (Astro 7 + CSS por capas + KaTeX)

Sitio estático de **Sucesiones** (Gustavo A. Duffour, *Matemática de Quinto*, cap.
«Nociones sobre sucesiones», pp. 101‑127). Astro 7, CSS vanilla con `@layer`, KaTeX
renderizado en build (cero JS cliente para mates), pnpm.

Plantilla copiada y adaptada de `~/GeomAnal` (mismo aspecto: papel + tinta magenta).

## Comandos (pnpm — no usar npm/yarn/bun)

| Comando          | Qué hace                              |
| ---------------- | ------------------------------------- |
| `pnpm dev`       | Servidor de desarrollo (`:4321`)      |
| `pnpm build`     | `astro check && astro build`          |
| `pnpm preview`   | Sirve `dist/` para verificar el build |
| `pnpm check`     | Solo chequeo de tipos                 |
| `pnpm approve-builds` | Autorizar scripts de build (esbuild, sharp) |

Requisito: Node ≥ 22.12 (Astro 7 no soporta Node 20), pnpm ≥ 9.

## ⚠️ PELIGRO: `@astrojs/compiler-rs` y los backslashes de KaTeX

**No quitar el override de `pnpm-workspace.yaml`:**

```yaml
overrides:
  '@astrojs/compiler-rs': 0.4.0
```

Con `0.4.1` el compilador nativo interpreta `\t`, `\b`, `\f` de los atributos como
secuencias de escape: `tex="\text{hola}"` llega a KaTeX como **TAB + `ext{hola}`**,
`\boxed` pierde la b (backspace) y `\frac` la f (form feed). Señales: fórmulas en
rojo, mensajes `unicodeTextInMathMode` en el build y caracteres de control
(0x08/0x09/0x0c) en `dist/**/*.html`.

Comprobación rápida tras cualquier cambio de dependencias:

```bash
python3 -c "
import glob
for f in sorted(glob.glob('dist/**/*.html', recursive=True)):
    s = open(f, encoding='utf8').read()
    print(f, {hex(ord(c)): s.count(c) for c in set(s) if ord(c) < 32 and c != chr(10)} or 'OK')"
```

Debe salir **OK** en todos los ficheros. `astro` está fijado a `7.3.2` (igual que
GeomAnal) para no arrastrar cambios de compilador.

## Notas de Astro 7 (migración desde v5)

1. `compressHTML: true` fijado en `astro.config.mjs`: el default v7 (`'jsx'`)
   pega palabras alrededor de elementos inline y rompería el math inline
   (`<Math display={false} />`) en los párrafos. No quitar sin revisar.
2. `markdown.processor: unified({...})` explícito + dependencia
   `@astrojs/markdown-remark`: Sätteri (default v7) no entiende remark/rehype.
   Reservado para futuro `.md`/`.mdx`.
3. El compilador Rust es estricto: etiquetas sin cerrar = error de build; no
   reordena HTML inválido. Revisar el build, no el navegador.
4. Sin flags `experimental`, sin `@astrojs/db`, sin `src/fetch.ts`.

## Arquitectura

```
src/
  pages/          # index.astro (/), capitulo-1..4.astro, formulas.astro,
                  # practico-sucesiones.astro (/practico-sucesiones)
  layouts/        # BaseLayout.astro (head, skip-link, favicon, .wrap)
  components/     # .astro estáticos por defecto (cero JS)
    Math.astro, Formula.astro, FormulaCard.astro, Nota.astro,
    Figura.astro, Split.astro, Masthead.astro, ChipsNav.astro,
    Topbar.astro, Hero.astro, Toc.astro, Seccion.astro, ChapterNav.astro,
    CalculatorShell.astro, MiniGrafico.astro (SVG de la 116, generado en build)
    calculators/  # Islas: CalcAritmetica, CalcGeometrica, CalcRecurrencia,
                  #        CalcFibonacci, RevealSolucion
  styles/         # global.css importa tokens → base → components (+ KaTeX);
                  # capitulo1.css (tema lector) y formulas.css (portada/fórmulas)
public/assets/sprites.svg   # 10 figuras (suc-*)
public/assets/favicon.svg
```

El **práctico** (`practico-sucesiones.astro`) transcribe §11 (preguntas), §12
(ejercicios 97‑116) y §13 (problemas 117‑126). Las soluciones son propias (el PDF
fuente no trae las páginas 475‑477) y van en el slot de `RevealSolucion`.

Fuente histórica (no commitear cambios, es el original): `Sucesiones.pdf`
(27 págs., pp. 101‑127). El PDF **no incluye** las páginas de resultados 475‑477:
toda solución del sitio está calculada por nosotros.

## Reglas de Astro (buenas prácticas aplicadas)

1. **Cero JS por defecto.** Todo componente es estático. La interactividad vive
   en el `<script>` propio de cada componente `.astro`. Las directivas `client:*`
   son solo para componentes de framework; **nunca** en componentes `.astro`.
2. **Sin `Astro.glob()` ni `entry.render()`** (APIs obsoletas).
3. **`RevealSolucion` tiene dos modos:** prop `solucion` (texto plano escrito en
   el `<output>`, como en los capítulos) o **slot** (panel `hidden` con KaTeX y
   listas, como en el práctico). El botón siempre es `button[data-reveal]` y
   conmuta `aria-expanded`; `scripts/verificar.py` prueba los dos.
4. **Rutas finas:** las páginas ensamblan layouts + componentes.
5. **Props tipadas** con `interface Props`. `set:html` solo para salida saneada
   (KaTeX) o `tituloHtml` interno — nunca con input de usuario.
6. **Figuras:** sprite vía `<Figura>`; `role="img"` + `aria-label` siempre;
   `output[aria-live="polite"]` en calculadoras.

## Reglas de CSS

1. **Orden de cascada fijo:** `@layer tokens, reset, base, components, page`
   (declarado en `global.css`). Los temas solo aportan `@layer page`.
2. **Tokens primero** en `tokens.css`. Prohibidos valores mágicos y `!important`.
3. **Especificidad 0 en base:** `:where()`, propiedades lógicas, nesting nativo.
4. **Estilos scoped:** el `<style>` de un `.astro` queda scropeado; si el nodo se
   crea desde JS (p. ej. el SVG de `CalcRecurrencia`) usar `:global(...)`.
5. **Responsive mobile-first:** `40rem` móvil · `48rem` tablet · `64rem` desktop.
6. **Accesibilidad:** `:focus-visible`, `skip-link`, `prefers-reduced-motion`,
   `.katex-display` con `overflow-x: auto` (nunca recortar fórmulas).

## Reglas de mates (KaTeX)

1. Toda fórmula pasa por `<Math tex="…" />` (`display=true` bloque con
   `.formula`, `false` inline). **Sin delimitadores** `$` ni `\(` en `tex`.
   **Un solo backslash** en todo comando: `tex="\frac{a}{b} \boxed{x}"`.
   (Válido mientras rija el override de `compiler-rs` 0.4.0; ver arriba.)
2. KaTeX ≠ MathJax: no existe `\sen` → usar `\operatorname{sen}`;
   `\boxed{}`, `\text{}`, `\operatorname{}`, `aligned`, `cases`, `sum` con
   límites sí soportados.
3. El CSS de KaTeX se importa una vez en `global.css`. Sin CDN de MathJax.
4. Tras tocar fórmulas: `pnpm build` debe terminar **sin avisos
   `LaTeX-incompatible input`** y sin `color:#cc0000` en `dist/`.

## Reglas de JS en islas

1. Sin `onclick` inline ni `<script>` global: cada isla lleva su propio
   `<script>` con `addEventListener("submit")` sobre `form[data-calc]`.
2. `<form>` + `<button type="submit">` (funciona con teclado y Enter);
   `input[type="number"]` con `name` estable; dejar un campo vacío = despejarlo.
3. Resultado siempre en `<output aria-live="polite">`.

## Búsqueda de código (usar obligatoriamente tgrep en vez de grep/rg)

`tgrep` es el buscador estándar del proyecto (índice de trigramas en `.tgrep/`).

1. Este directorio **no debe indexar `node_modules/`**: pasar siempre
   `--no-require-git` en `index`, `serve` y cada búsqueda. Mantener el índice al
   día: `tgrep index . --no-require-git`.
2. Orden de argumentos: flags primero, `--` después:
   `tgrep --no-require-git -l -F -- "CalcAritmetica" .`
3. `-F` para símbolos/literales, `-g '*.astro'` para acotar, `-l` primero en
   consultas amplias. Exit codes: `1` = sin resultados, `2` = error.
4. El índice no ve ediciones posteriores: añadir `--no-index` si el resultado
   debe reflejar el último cambio.

## Skills de agente (autoskills — https://www.autoskills.sh/)

`npx autoskills` detecta el stack desde `package.json` y la config e instala
skills curadas (hashes en `skills-lock.json`; no editar a mano, se regeneran con
`npx autoskills`). Instaladas en `.agents/skills/`: `astro`,
`typescript-advanced-types`, `frontend-design`, `accessibility`, `seo`.
Ante conflicto entre una skill genérica y este `AGENTS.md`, **manda este fichero**
(backslash simple en KaTeX, `compressHTML: true`, override del compilador,
nunca `client:*` en `.astro`).

## Definición de hecho (antes de dar por hecha una tarea)

1. `pnpm build` en verde, **cero avisos de KaTeX** y sin caracteres de control
   en `dist/` (comprobación arriba).
2. `pnpm preview` + script de verificación (Playwright con `channel="chrome"`):
   sin scroll horizontal a 360/768/1280 px en las 7 rutas, calculadoras
   respondiendo por teclado y `RevealSolucion` mostrando la solución (modo texto
   en los capítulos y panel con KaTeX en el práctico).
3. Repasar en `pnpm dev` que ninguna fórmula sale en rojo.

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->
