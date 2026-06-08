"""Diagnóstico do layout do 'Extrato de Movimentação' da B3.

Uso:
    python scripts/inspecionar_extrato.py samples/extrato.pdf

Imprime, por página: palavras com coordenadas e os marcadores coloridos
(curvas/retângulos preenchidos) com suas cores, para calibrar a detecção
de compra (verde) vs. venda (laranja/vermelho).
"""

from __future__ import annotations

import sys

import pdfplumber


def main(caminho: str) -> None:
    with pdfplumber.open(caminho) as pdf:
        for i, pagina in enumerate(pdf.pages, start=1):
            print(f"\n===== PÁGINA {i} =====")
            print("--- PALAVRAS (texto | x0 | x1 | top) ---")
            for w in pagina.extract_words():
                print(f"{w['text']!r:40} x0={w['x0']:.1f} x1={w['x1']:.1f} top={w['top']:.1f}")

            print("\n--- CURVAS PREENCHIDAS (cor | top | x0) ---")
            for c in pagina.curves:
                if c.get("fill"):
                    print(f"fill={c.get('non_stroking_color')} top={c.get('top'):.1f} x0={c.get('x0'):.1f}")

            print("\n--- RETÂNGULOS PREENCHIDOS (cor | top | x0) ---")
            for r in pagina.rects:
                if r.get("fill"):
                    print(f"fill={r.get('non_stroking_color')} top={r.get('top'):.1f} x0={r.get('x0'):.1f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Informe o caminho do PDF. Ex.: python scripts/inspecionar_extrato.py samples/extrato.pdf")
        raise SystemExit(1)
    main(sys.argv[1])
