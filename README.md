# Apuntes guía (Quarto Book) — Publicación y Edición Web

Este repositorio publica un libro Quarto (tipo _book_) en GitHub Pages.
El flujo está pensado para trabajar solo desde el navegador: editas archivos `.qmd` en GitHub y una GitHub Action compila y despliega automáticamente.

URL del sitio (una vez publicado): https://elgeografo.github.io/dibujo/

---

## Tabla de contenidos

- Estructura básica
- Publicación automática (workflow)
- Configuración inicial
  - GitHub Pages
  - GitHub Action de Quarto
- Cómo editar contenido (100% web)
  - Añadir un capítulo nuevo
- Ajustes útiles de Quarto
- Solución de problemas
- Soporte Python (opcional)
- Checklist rápido
- Autores y afiliación

---

## Estructura básica

- `_quarto.yml` → configuración del libro (título, capítulos, tema, etc.)
- `index.qmd` → portada del libro
- Otros capítulos `.qmd` (por ejemplo `01-normalizacion.qmd`, `01-04-proyecciones.qmd`, `03-geometria-constructiva.qmd`, …)
- `.github/workflows/quarto-publish.yml` → workflow que compila y publica

Nota: Los capítulos listados en `_quarto.yml` deben existir para que el build pase. Si falta alguno, crea un placeholder con un mínimo de contenido.

---

## Publicación automática (workflow)

1. Edita cualquier `.qmd` desde el navegador (botón “Edit”).
2. Haz Commit.
3. La pestaña Actions ejecutará: “Build & Publish Quarto Book to GitHub Pages”.
4. Al terminar, el sitio se actualiza en la rama `gh-pages` y queda visible en: https://elgeografo.github.io/dibujo/

También puedes lanzarlo manualmente: Actions → “Build & Publish…” → “Run workflow”.

---

## Configuración inicial

### GitHub Pages

En Settings → Pages del repositorio:
- Build and deployment → Source: “Deploy from a branch”
- Branch: `gh-pages` y carpeta `/ (root)`

### GitHub Action de Quarto

Archivo: `.github/workflows/quarto-publish.yml`

(Contenido de ejemplo; ajusta paquetes de R si necesitas más)

    name: Build & Publish Quarto Book to GitHub Pages

    on:
      push:
        branches: [ main ]
      workflow_dispatch: {}

    permissions:
      contents: write
      pages: write
      id-token: write

    jobs:
      build-deploy:
        runs-on: ubuntu-latest

        steps:
          - name: Checkout repo
            uses: actions/checkout@v4

          - name: Setup Quarto
            uses: quarto-dev/quarto-actions/setup@v2

          # 1) Instalar R
          - name: Setup R
            uses: r-lib/actions/setup-r@v2
            with:
              use-public-rspm: true

          # 2) Paquetes de R necesarios (ajusta la lista si hace falta)
          - name: Install R packages
            run: |
              Rscript -e 'install.packages(c(
                "knitr",
                "rmarkdown",
                "ggplot2",
                "dplyr",
                "readr"
              ))'

          - name: Render Book
            uses: quarto-dev/quarto-actions/render@v2
            with:
              path: .

          - name: Publish to GitHub Pages (gh-pages)
            uses: quarto-dev/quarto-actions/publish@v2
            with:
              target: gh-pages
            env:
              GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

---

## Cómo editar contenido (100% web)

1. Abre el archivo `.qmd` que quieras modificar.
2. Clic en “Edit” (icono de lápiz).
3. Escribe en Markdown/Quarto (títulos `#`, bloques de código, etc.).
4. “Commit changes”.
5. Espera a que la Action termine → los cambios aparecen en la web.

### Añadir un capítulo nuevo

1. Crea un archivo (p. ej. `04-nuevo-capitulo.qmd`) con contenido mínimo:

    ---
    title: "Nuevo capítulo"
    ---

    # Nuevo capítulo

    Contenido en construcción.

2. En `_quarto.yml`, añade el archivo en `book: chapters:`:

    book:
      chapters:
        - index.qmd
        - 01-normalizacion.qmd
        - 01-04-proyecciones.qmd
        - 03-geometria-constructiva.qmd
        - 04-nuevo-capitulo.qmd   # ← añadido

3. Commit y listo.

---

## Ajustes útiles de Quarto

- Congelar resultados (acelera builds y evita reevaluar chunks sin cambios):

    execute:
      freeze: auto

- TOC, numeración, botones de copiar código: ajusta `format: html:` en `_quarto.yml` según necesites.  
  (La configuración actual usa el tema `cosmo` + `r4ds.scss`, numeración de secciones y `code-link` activados.)
- Estilos propios: puedes añadir CSS personalizado y referenciarlo desde `_quarto.yml`.

---

## Solución de problemas

1) “Unable to locate an installed version of R / Error executing 'Rscript'”
   - La Action no encuentra R. Confirma que el paso “Setup R” y “Install R packages” están en el workflow.

2) “there is no package called ‘xxx’”
   - Falta un paquete de R. Añádelo en el paso Install R packages, por ejemplo:
     Rscript -e 'install.packages(c("knitr","ggplot2","dplyr","readr","xxx"))'

3) Faltan capítulos listados en `_quarto.yml`
   - El build falla si un archivo declarado no existe. Crea el `.qmd` faltante o comenta su línea en `chapters`.

4) Publica pero no veo cambios
   - Revisa Actions (que el job termine en verde).
   - En Settings → Pages, confirma la fuente `gh-pages / (root)`.
   - Forzar deploy: en Actions, pulsa “Run workflow”.

5) Paquetes con dependencias del sistema (geoespacial, etc.)
   - Si usas `sf`, `terra`, `rgdal`, etc., requieren librerías del sistema. Será necesario añadir un paso `apt-get` antes de instalar esos paquetes.

---

## Soporte Python (opcional)

Si mezclas chunks de Python, añade antes de “Render Book”:

    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install Python deps
      run: |
        pip install -r requirements.txt

Y crea un `requirements.txt` con las librerías que uses.

---

## Checklist rápido

- [_] `_quarto.yml` (tipo `book`) bien configurado y capítulos existentes  
- [_] Pages: `gh-pages / (root)`  
- [_] Workflow en `.github/workflows/quarto-publish.yml`  
- [_] Instalar R + paquetes necesarios en la Action  
- [_] Commit → Actions OK → sitio actualizado

---

## Autores y afiliación

(Coloca la imagen en `images/authors2.png`)

[Imagen autores (no clicable aquí)]
images/authors2.png

Grupo de investigación GEOSO2 — Universidad Politécnica de Madrid
Web: https://www.geoso2.es

