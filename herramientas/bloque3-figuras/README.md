# Generadores de las figuras SVG del Bloque 3 (planos acotados)

Todo el material didáctico del Bloque 3 (decks Reveal y capítulos) usa SVG
con geometría **calculada** por estos scripts. El terreno conductor del
bloque (dos cerros y un collado) está definido en `terreno.py`.

## Flujo de trabajo

```bash
python3 terreno.py        # regenera contornos.json (curvas de nivel del terreno)
python3 fig_intro.py      # figuras del tema 1 -> svg/*.svg
python3 fig_fund.py       # tema 2 (punto, recta, plano, graduación)
python3 fig_plano3.py     # tema 3 (definición de planos, vaguadas)
python3 fig_perfil.py     # tema 4 (perfiles)
python3 fig_expla.py      # tema 5 (explanaciones)

# ensamblar un qmd final sustituyendo {{SVG:nombre}} por svg/nombre.svg
python3 build.py templates/acotados-1-introduccion.qmd ../../presentaciones/acotados-1-introduccion.qmd
```

**Ojo**: los `.qmd` del repositorio (en `presentaciones/` y `03-planos-acotados/`)
son los archivos construidos y son la fuente que renderiza Quarto. Las
plantillas de `templates/` + los SVG generados son su origen: si se edita una
plantilla o un script de figuras, hay que reconstruir el `.qmd` con `build.py`.
Si se retoca un `.qmd` construido directamente, conviene replicar el cambio
en su plantilla.

Requisitos: Python 3 con numpy y matplotlib (solo para extraer curvas de nivel
y tintas hipsométricas; los SVG se escriben a mano por los scripts).

Cada figura tiene dos variantes: `nombre.svg` (con fragmentos Reveal
`data-fragment-index` para la presentación) y `nombre_static.svg` (todo
visible, para los capítulos del libro).
