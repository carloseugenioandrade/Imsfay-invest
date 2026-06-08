"""Importador de extratos da B3 / corretoras (XLSX e PDF).

O usuário faz upload do relatório de "Negociação" da Área do Investidor da B3
(ou extrato da corretora) em XLSX ou PDF; o parser normaliza colunas e devolve
transações prontas para inserir em `transacoes`.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime
from io import BytesIO

import pandas as pd


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.strip().lower()


def _achar_coluna(colunas: dict[str, str], *chaves: str) -> str | None:
    for norm, original in colunas.items():
        if any(chave in norm for chave in chaves):
            return original
    return None


def _extrair_ticker(valor: str) -> str:
    # "PETR4 - PETROBRAS PN" -> "PETR4"; "PETR4" -> "PETR4".
    return str(valor).split(" - ")[0].strip().upper()


def _parse_data(valor) -> date | None:
    if isinstance(valor, (datetime, pd.Timestamp)):
        return valor.date()
    if isinstance(valor, date):
        return valor
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(str(valor).strip(), fmt).date()
        except ValueError:
            continue
    return None


def _to_float(valor) -> float | None:
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    s = str(valor).strip().replace("R$", "").replace(" ", "")
    if not s:
        return None
    # Trata formato brasileiro 1.234,56.
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _classificar_tipo(valor) -> str:
    tipo_raw = _normalizar(valor) if valor is not None else "compra"
    if tipo_raw.startswith("v") or "venda" in tipo_raw or "debito" in tipo_raw:
        return "VENDA"
    return "COMPRA"


def _processar_dataframe(df: pd.DataFrame) -> list[dict]:
    """Normaliza um DataFrame de negociação (de XLSX ou de tabela de PDF) em
    transações. Cada item: {ticker, tipo_operacao, data_operacao, quantidade,
    preco_unitario}.
    """
    if df.empty:
        return []

    colunas = {_normalizar(c): c for c in df.columns}
    col_data = _achar_coluna(colunas, "data do negocio", "data negocio", "data")
    col_ticker = _achar_coluna(colunas, "codigo de negociacao", "codigo", "produto", "ativo", "papel")
    col_tipo = _achar_coluna(colunas, "tipo de movimentacao", "compra/venda", "c/v", "movimentacao", "tipo")
    col_qtd = _achar_coluna(colunas, "quantidade", "qtde")
    col_preco = _achar_coluna(colunas, "preco unitario", "preco", "preço")

    if not (col_data and col_ticker and col_qtd and col_preco):
        return []

    transacoes: list[dict] = []
    for _, linha in df.iterrows():
        data_op = _parse_data(linha.get(col_data))
        ticker = _extrair_ticker(linha.get(col_ticker, ""))
        quantidade = _to_float(linha.get(col_qtd))
        preco = _to_float(linha.get(col_preco))
        if not data_op or not ticker or not quantidade or preco is None:
            continue

        transacoes.append({
            "ticker": ticker,
            "tipo_operacao": _classificar_tipo(linha.get(col_tipo) if col_tipo else None),
            "data_operacao": data_op,
            "quantidade": abs(quantidade),
            "preco_unitario": preco,
        })
    return transacoes


def parse_extrato_xlsx(conteudo: bytes) -> list[dict]:
    """Lê um XLSX de negociação e retorna transações normalizadas."""
    return _processar_dataframe(pd.read_excel(BytesIO(conteudo)))


# Linha típica de nota de negociação / extrato textual:
#   "10/01/2024 C PETR4 100 30,50"  ou  "10/01/2024 Compra PETR4 100 R$ 30,50"
_TICKER_RE = r"[A-Z]{4}\d{1,2}|[A-Z]{4}\d{1,2}[A-Z]?"
_LINHA_RE = re.compile(
    r"(?P<data>\d{2}/\d{2}/\d{4})"
    r"\s+(?P<tipo>C|V|compra|venda|comprada?|vendida?)\b"
    r"\s+(?P<ticker>[A-Z]{4}\d{1,2}[A-Z]?)\b"
    r".*?(?P<quantidade>[\d.]+)"
    r"\s+(?:R\$\s*)?(?P<preco>[\d.]+,\d{2})",
    re.IGNORECASE,
)


def _parse_pdf_texto(texto: str) -> list[dict]:
    """Fallback: extrai transações de PDFs baseados em texto livre (notas de
    corretagem) usando regex linha a linha."""
    transacoes: list[dict] = []
    for match in _LINHA_RE.finditer(texto):
        data_op = _parse_data(match.group("data"))
        ticker = _extrair_ticker(match.group("ticker"))
        quantidade = _to_float(match.group("quantidade"))
        preco = _to_float(match.group("preco"))
        if not data_op or not ticker or not quantidade or preco is None:
            continue
        transacoes.append({
            "ticker": ticker,
            "tipo_operacao": _classificar_tipo(match.group("tipo")),
            "data_operacao": data_op,
            "quantidade": abs(quantidade),
            "preco_unitario": preco,
        })
    return transacoes


_MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "abril": 4, "maio": 5, "junho": 6,
    "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}
_DATA_EXT_RE = re.compile(r"^(\d{1,2})\s+de\s+([a-zç]+)\s+de\s+(\d{4})$")
_NUM_RE = re.compile(r"^\d{1,3}(?:\.\d{3})+(?:,\d+)?$|^\d+(?:,\d+)?$")
_MOVIMENTOS = {"venda", "compra", "transferencia"}


def _parse_data_extenso(texto: str) -> date | None:
    m = _DATA_EXT_RE.match(_normalizar(texto))
    if not m:
        return None
    dia, mes_nome, ano = m.groups()
    mes = _MESES.get(mes_nome)
    return date(int(ano), mes, int(dia)) if mes else None


def _cor_marcador(col) -> str | None:
    """Verde = COMPRA (entrada), vermelho/laranja = VENDA (saída)."""
    if not isinstance(col, (list, tuple)) or len(col) != 3:
        return None
    r, g, b = col
    if g > 0.4 and r < 0.3:
        return "COMPRA"
    if r > 0.6 and g < 0.45:
        return "VENDA"
    return None


def _classificar_ativo(ticker: str) -> str:
    t = ticker.upper()
    if t.startswith("TESOURO"):
        return "Tesouro"
    if re.match(r"^[A-Z]{4}11$", t):
        return "FII"
    return "Acao"


def _clusterizar_linhas(words: list[dict], tol: float = 2.5) -> list[dict]:
    """Agrupa palavras em linhas pelo topo (tolerância em pontos)."""
    linhas: list[dict] = []
    for w in sorted(words, key=lambda x: (x["top"], x["x0"])):
        if linhas and abs(w["top"] - linhas[-1]["top"]) <= tol:
            linhas[-1]["words"].append(w)
        else:
            linhas.append({"top": w["top"], "words": [w]})
    return linhas


def _parse_pagina_movimentacao(pagina) -> list[dict]:
    """Parser do 'Extrato de Movimentação' da B3 (data no cabeçalho, colunas
    posicionais e direção compra/venda pela cor do marcador)."""
    linhas = _clusterizar_linhas(pagina.extract_words())
    marcadores = []
    for c in pagina.curves:
        tipo = _cor_marcador(c.get("non_stroking_color"))
        if tipo and c.get("x0", 99) < 60:
            marcadores.append((c["top"], tipo))

    # Classifica cada linha e localiza inícios de transação.
    eventos: list[tuple[int, str]] = []
    cols = {"prod": 100.0, "inst": 230.0}
    for i, ln in enumerate(linhas):
        textos = [w["text"] for w in ln["words"]]
        joined = " ".join(textos)
        if _parse_data_extenso(joined):
            eventos.append((i, "data"))
        elif "Produto" in textos and "Quantidade" in textos:
            eventos.append((i, "header"))
        elif textos and _normalizar(textos[0]) in _MOVIMENTOS and ln["words"][0]["x0"] < 110:
            eventos.append((i, "txn"))
        elif textos and textos[0].lower().startswith("acesse"):
            eventos.append((i, "footer"))

    transacoes: list[dict] = []
    data_atual: date | None = None
    for idx, (li, tipo_ev) in enumerate(eventos):
        ln = linhas[li]
        if tipo_ev == "data":
            data_atual = _parse_data_extenso(" ".join(w["text"] for w in ln["words"]))
        elif tipo_ev == "header":
            for w in ln["words"]:
                if w["text"] == "Produto":
                    cols["prod"] = w["x0"]
                elif w["text"] == "Instituição":
                    cols["inst"] = w["x0"]
        elif tipo_ev == "txn":
            fim = linhas[eventos[idx + 1][0]]["top"] if idx + 1 < len(eventos) else 1e9
            banda = [w for w in pagina.extract_words() if ln["top"] - 1 <= w["top"] < fim - 1]
            t = _montar_transacao(banda, cols, data_atual, ln["top"], marcadores, ln["words"])
            if t:
                transacoes.append(t)
    return transacoes


def _montar_transacao(banda, cols, data_atual, top, marcadores, words_inicio):
    if data_atual is None:
        return None
    # Produto (ticker) entre as colunas Produto e Instituição.
    prod = [w for w in banda if cols["prod"] - 6 <= w["x0"] < cols["inst"] - 6]
    prod.sort(key=lambda w: (w["top"], w["x0"]))
    ticker = _extrair_ticker(" ".join(w["text"] for w in prod))
    # Colunas numéricas por faixa de x fixa.
    qtd = preco = None
    for w in sorted(banda, key=lambda w: w["x0"]):
        if not _NUM_RE.match(w["text"]):
            continue
        if 395 < w["x0"] < 452 and qtd is None:
            qtd = _to_float(w["text"])
        elif 452 <= w["x0"] < 515 and preco is None:
            preco = _to_float(w["text"])
    if not ticker or not qtd or preco is None:
        return None
    # Direção pela cor do marcador mais próximo; fallback pela palavra.
    tipo = None
    melhor = 15.0
    for mtop, mtipo in marcadores:
        if abs(mtop - top) < melhor:
            melhor, tipo = abs(mtop - top), mtipo
    if tipo is None:
        tipo = _classificar_tipo(words_inicio[0]["text"])
    return {
        "ticker": ticker,
        "tipo_operacao": tipo,
        "data_operacao": data_atual,
        "quantidade": abs(qtd),
        "preco_unitario": preco,
        "tipo_ativo": _classificar_ativo(ticker),
    }


def parse_extrato_pdf(conteudo: bytes) -> list[dict]:
    """Lê um PDF da B3. Tenta o layout 'Extrato de Movimentação'; se não
    reconhecer, faz fallback para tabelas estruturadas. Requer `pdfplumber`."""
    try:
        import pdfplumber
    except ImportError as exc:  # pragma: no cover - dependência opcional
        raise RuntimeError(
            "Suporte a PDF requer 'pdfplumber'. Rode: pip install pdfplumber"
        ) from exc

    transacoes: list[dict] = []
    with pdfplumber.open(BytesIO(conteudo)) as pdf:
        for pagina in pdf.pages:
            transacoes.extend(_parse_pagina_movimentacao(pagina))
        if transacoes:
            return transacoes
        # Fallback: relatório de Negociação em formato de tabela.
        for pagina in pdf.pages:
            for tabela in pagina.extract_tables() or []:
                if not tabela or len(tabela) < 2:
                    continue
                cabecalho, *linhas = tabela
                colunas = [str(c or f"col{i}") for i, c in enumerate(cabecalho)]
                transacoes.extend(_processar_dataframe(pd.DataFrame(linhas, columns=colunas)))
    return transacoes
