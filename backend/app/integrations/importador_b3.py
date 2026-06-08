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


def parse_extrato_pdf(conteudo: bytes) -> list[dict]:
    """Lê um PDF de negociação (relatório B3 ou nota de corretagem).

    Estratégia: primeiro tenta extrair tabelas estruturadas (mesma lógica do
    XLSX); se não reconhecer colunas, faz fallback para parsing textual via
    regex. Requer `pdfplumber`.
    """
    try:
        import pdfplumber
    except ImportError as exc:  # pragma: no cover - dependência opcional
        raise RuntimeError(
            "Suporte a PDF requer 'pdfplumber'. Rode: pip install pdfplumber"
        ) from exc

    transacoes: list[dict] = []
    textos: list[str] = []
    with pdfplumber.open(BytesIO(conteudo)) as pdf:
        for pagina in pdf.pages:
            for tabela in pagina.extract_tables() or []:
                if not tabela or len(tabela) < 2:
                    continue
                cabecalho, *linhas = tabela
                colunas = [str(c or f"col{i}") for i, c in enumerate(cabecalho)]
                df = pd.DataFrame(linhas, columns=colunas)
                transacoes.extend(_processar_dataframe(df))
            texto = pagina.extract_text() or ""
            if texto:
                textos.append(texto)

    # Deduplica resultados das tabelas (mesma transação aparecendo 2x).
    vistos = {tuple(t.items()) for t in transacoes}

    if not transacoes:
        transacoes = _parse_pdf_texto("\n".join(textos))
    else:
        # Complementa com linhas textuais ainda não capturadas.
        for t in _parse_pdf_texto("\n".join(textos)):
            if tuple(t.items()) not in vistos:
                transacoes.append(t)
                vistos.add(tuple(t.items()))

    return transacoes
