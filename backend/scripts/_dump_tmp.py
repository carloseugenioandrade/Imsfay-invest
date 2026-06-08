import pdfplumber

path = "samples/movimentacao-2026-06-07-22-16-20.pdf"
with open("samples/_dump.txt", "w", encoding="utf-8") as out:
    with pdfplumber.open(path) as pdf:
        for i, p in enumerate(pdf.pages, 1):
            out.write(f"===== PAGINA {i} =====\n")
            for w in p.extract_words():
                out.write(f"W {w['text']!r} x0={w['x0']:.1f} x1={w['x1']:.1f} top={w['top']:.1f}\n")
            out.write("--CURVES (nao-cinza)--\n")
            for c in p.curves:
                col = c.get("non_stroking_color")
                # ignora cinza claro das bordas
                if col and not (isinstance(col, (list, tuple)) and len(col) == 3 and all(v > 0.8 for v in col)):
                    out.write(f"C fill={col} top={c['top']:.1f} x0={c['x0']:.1f} x1={c['x1']:.1f}\n")
print("ok")
