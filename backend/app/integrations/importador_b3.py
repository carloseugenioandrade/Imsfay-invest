"""Importador de extratos da B3 / corretoras (XLSX).

O usuário faz upload do relatório de "Negociação" da Área do Investidor da B3
(ou extrato da corretora); o parser normaliza colunas e devolve transações
prontas para inserir em `transacoes`.
"""

from __future__ import annotations

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


def parse_extrato_xlsx(conteudo: bytes) -> list[dict]:
    """Lê um XLSX de negociação e retorna transações normalizadas.

    Cada item: {ticker, tipo_operacao(COMPRA/VENDA), data_operacao,
    quantidade, preco_unitario}.
    """
    df = pd.read_excel(BytesIO(conteudo))
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

        tipo_raw = _normalizar(linha.get(col_tipo, "")) if col_tipo else "compra"
        if tipo_raw.startswith("v") or "venda" in tipo_raw or "debito" in tipo_raw:
            tipo = "VENDA"
        else:
            tipo = "COMPRA"

        transacoes.append({
            "ticker": ticker,
            "tipo_operacao": tipo,
            "data_operacao": data_op,
            "quantidade": abs(quantidade),
            "preco_unitario": preco,
        })
    return transacoes
