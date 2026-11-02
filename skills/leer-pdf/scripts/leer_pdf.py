#!/usr/bin/env python3
"""Lee un PDF (URL o archivo local) y devuelve su texto por página, con OCR en español e inglés.

Uso:
  python leer_pdf.py FUENTE [--paginas 24 | 20-30 | 1,5,9] [--buscar REGEX]
                            [--ocr auto|si|no] [--idiomas spa+eng] [--imagenes CARPETA]

- Texto: pypdf. Si una página casi no tiene texto (escaneada), OCR con Tesseract.
- --buscar: muestra solo los fragmentos que coinciden, con su página, para citar.
- --imagenes: guarda las páginas como PNG para leerlas con la herramienta Read (tablas, gráficos).
- Las URLs se descargan en una carpeta temporal aislada. No ejecuta nada del PDF.

Licencias de las dependencias: pypdf (BSD-3-Clause), pypdfium2 (BSD-3-Clause / Apache-2.0),
pytesseract y Tesseract OCR (Apache-2.0).
"""
import argparse
import os
import re
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

WINDOWS_TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
TESSERACT = Path(os.environ.get("TESSERACT_EXE")
                 or shutil.which("tesseract")
                 or WINDOWS_TESSERACT)
# Carpeta con spa/eng .traineddata. Si no existe, Tesseract usa su carpeta por defecto.
TESSDATA = Path(os.environ.get("TESSDATA_DIR", Path.home() / "tessdata"))
MINIMO_TEXTO = 50  # caracteres; menos que esto = página escaneada


def obtener(fuente: str) -> Path:
    if re.match(r"^https?://", fuente, re.I):
        carpeta = Path(tempfile.mkdtemp(prefix="leer-pdf-"))
        destino = carpeta / "documento.pdf"
        pedido = urllib.request.Request(fuente, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(pedido, timeout=120) as r:
            destino.write_bytes(r.read())
        return destino
    ruta = Path(fuente).expanduser()
    if not ruta.is_file():
        sys.exit(f"No existe el archivo: {ruta}")
    return ruta


def rango(texto: str, total: int) -> list:
    if not texto:
        return list(range(1, total + 1))
    paginas = set()
    for parte in texto.split(","):
        if "-" in parte:
            a, b = parte.split("-", 1)
            paginas.update(range(int(a), int(b) + 1))
        else:
            paginas.add(int(parte))
    return sorted(p for p in paginas if 1 <= p <= total)


def ocr(pdfium_doc, numero: int, idiomas: str) -> str:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT)
    if TESSDATA.is_dir():
        os.environ["TESSDATA_PREFIX"] = str(TESSDATA)  # en Windows, --tessdata-dir con comillas falla
    imagen = pdfium_doc[numero - 1].render(scale=300 / 72).to_pil()
    return pytesseract.image_to_string(imagen, lang=idiomas)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("fuente", help="URL o ruta del PDF")
    p.add_argument("--paginas", default="", help="24 | 20-30 | 1,5,9 (por defecto, todas)")
    p.add_argument("--buscar", default="", help="Expresión regular; muestra solo coincidencias con su página")
    p.add_argument("--ocr", choices=["auto", "si", "no"], default="auto")
    p.add_argument("--idiomas", default="spa+eng")
    p.add_argument("--imagenes", default="", help="Carpeta donde guardar las páginas como PNG")
    a = p.parse_args()

    import pypdf
    import pypdfium2

    ruta = obtener(a.fuente)
    lector = pypdf.PdfReader(str(ruta))
    total = len(lector.pages)
    paginas = rango(a.paginas, total)
    pdfium_doc = pypdfium2.PdfDocument(str(ruta)) if (a.ocr != "no" or a.imagenes) else None
    print(f"# {a.fuente} — {total} páginas; leídas: {len(paginas)}")

    for n in paginas:
        texto = lector.pages[n - 1].extract_text() or ""
        metodo = "texto"
        if a.ocr == "si" or (a.ocr == "auto" and len(texto.strip()) < MINIMO_TEXTO):
            texto = ocr(pdfium_doc, n, a.idiomas)
            metodo = f"ocr {a.idiomas}"
        if a.imagenes:
            carpeta = Path(a.imagenes)
            carpeta.mkdir(parents=True, exist_ok=True)
            pdfium_doc[n - 1].render(scale=150 / 72).to_pil().save(carpeta / f"pagina-{n:03d}.png")
        if a.buscar:
            for m in re.finditer(rf".{{0,200}}(?:{a.buscar}).{{0,200}}", texto, re.S | re.I):
                print(f"--- p. {n} ({metodo}): {' '.join(m.group(0).split())}")
        else:
            print(f"\n=== p. {n} ({metodo}) ===\n{texto.strip()}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
