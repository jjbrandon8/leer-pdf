# leer-pdf

A Claude skill that reads PDFs (a URL or a local file) page by page, with OCR in Spanish and English, so every fact can be cited with its page.

[Español](#español) · [English](#english)

---

## Español

### Qué hace

- Extrae el texto de cada página. Si una página es escaneada, le aplica OCR solo.
- `--buscar "regex"` devuelve solo las coincidencias con su número de página, listas para citar.
- `--imagenes carpeta` guarda las páginas como PNG para que Claude lea tablas y gráficos.
- Descarga las URLs en una carpeta temporal aislada. No ejecuta nada del PDF.

### Licencias

Solo herramientas de código abierto con licencia permisiva: pypdf (BSD-3-Clause), pypdfium2 (BSD-3-Clause / Apache-2.0), pytesseract y Tesseract OCR (Apache-2.0), idiomas de `tessdata_fast` (Apache-2.0). No usa PyMuPDF (AGPL) ni Poppler (GPL).

### Instalar

1. Python 3.8 o superior, y `pip install pypdf pypdfium2 pytesseract`.
2. Tesseract OCR:
   - Windows: `winget install UB-Mannheim.TesseractOCR`
   - macOS: `brew install tesseract tesseract-lang`
   - Linux: `apt install tesseract-ocr tesseract-ocr-spa`
3. Si tu Tesseract no trae español, descarga `spa.traineddata` de https://github.com/tesseract-ocr/tessdata_fast en una carpeta `tessdata` de tu usuario, junto con `eng.traineddata`, o define `TESSDATA_DIR`.
4. La skill, en Claude Code:

```
/plugin marketplace add jjbrandon8/leer-pdf
/plugin install leer-pdf@jjbrandon8-leer-pdf
```

### Usar

```
python -I scripts/leer_pdf.py "https://ejemplo.gob.ec/informe.pdf" --buscar "proveedores"
python -I scripts/leer_pdf.py informe.pdf --paginas 20-30
```

O pídele a Claude: "lee este PDF y dime en qué página aparece X".

---

## English

Reads PDFs page by page with OCR in Spanish and English, using only permissively licensed open source tools. Install the Python packages `pypdf pypdfium2 pytesseract` and Tesseract OCR (Windows `winget install UB-Mannheim.TesseractOCR`, macOS `brew install tesseract tesseract-lang`, Linux `apt install tesseract-ocr tesseract-ocr-spa`), then add the plugin with the commands above. Use `--buscar` to find a phrase with its page, `--paginas` to read some pages, and `--imagenes` to save pages as PNG for tables and charts.

## License

MIT
