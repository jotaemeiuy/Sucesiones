# Sucesiones — Duffour

Sitio estático con el teórico de **Nociones sobre sucesiones** (Gustavo A. Duffour,
*Matemática de Quinto*, pp. 101‑127): definición, aritméticas, geométricas, límite,
Zenón y Fibonacci, con resumen de fórmulas y calculadoras interactivas.

🌐 **Demo:** https://sucesiones.vercel.app

## Rutas

| Ruta | Contenido |
| ---- | --------- |
| `/` | Portada (orden de lectura) |
| `/capitulo-1/` | §§1‑4 Definición, formas de definir, monotonía y gráfica |
| `/capitulo-2/` | §5 Sucesiones aritméticas |
| `/capitulo-3/` | §6 Sucesiones geométricas |
| `/capitulo-4/` | §§7‑10 Límite, paradoja de Zenón, problema de aplicación y Fibonacci |
| `/formulas/` | Resumen de fórmulas + 4 calculadoras |
| `/practico-sucesiones/` | §11 preguntas del teórico, ejercicios 97‑116 y problemas 117‑126, con solución desplegable |

Las soluciones del práctico son propias: el PDF fuente no incluye las páginas de
resultados (475‑477), así que están calculadas para el sitio.

## Stack

- Astro 7 (sitio estático, cero JS por defecto; la interactividad vive en el
  `<script>` de cada isla, sin hidratación)
- CSS vanilla con `@layer` (`tokens → reset → base → components → page`)
- KaTeX renderizado en build (sin JS cliente para los mates)
- pnpm · Node ≥ 22

Mismo aspecto que [GeomAnal](https://geoanalitica.vercel.app): papel amarillo +
tinta magenta `#bf2045`, tipografía monoespaciada de titular.

## Comandos (pnpm — no usar npm/yarn/bun)

| Comando | Qué hace |
| ------- | -------- |
| `pnpm dev` | Servidor de desarrollo (`:4321`) |
| `pnpm check` | Solo chequeo de tipos |
| `pnpm build` | `astro check && astro build` |
| `pnpm preview` | Sirve `dist/` para verificar el build |

Verificación (con `pnpm preview` en marcha):

```bash
python3 scripts/verificar.py   # scroll horizontal 360/768/1280 + calculadoras
```

## Estructura

```
src/
  pages/          # Una ruta por fichero
  layouts/        # BaseLayout.astro
  components/     # .astro estáticos + calculators/ (islas)
  styles/         # tokens → base → components + un tema por página
public/assets/sprites.svg   # 10 figuras SVG (suc-*)
public/assets/favicon.svg
```

⚠️ **No quitar el override `@astrojs/compiler-rs: 0.4.0`** de
`pnpm-workspace.yaml`: con `0.4.1` los backslashes de KaTeX (`\text`, `\boxed`,
`\frac`) se convierten en caracteres de control y se rompen todas las fórmulas.
Detalle en `AGENTS.md`.

## Despliegue

Vercel, proyecto `sucesiones`: preset **Astro**, build `pnpm build`, output
`dist`, Node 22. Cada push a `main` se publica solo.

## Fuente

`Sucesiones.pdf` (27 páginas) — material original del libro, usado como fuente
del contenido. Las figuras SVG están dibujadas a partir de las del libro.
