"""Cliente Yahoo Finance (via biblioteca `yfinance`).

Uso: dados fundamentalistas brutos (LPA, VPA, P/L, ROE, DY) e cotações
internacionais (Stocks, REITs, Cripto). Tickers da B3 usam sufixo `.SA`.
"""

from __future__ import annotations

import yfinance as yf


def _yahoo_symbol(ticker: str) -> str:
    """Adiciona sufixo .SA para tickers brasileiros (letras + dígitos)."""
    t = ticker.upper()
    if "." in t or "-" in t:
        return t
    if any(c.isdigit() for c in t):
        return f"{t}.SA"
    return t


def get_fundamentos(ticker: str) -> dict | None:
    """Normaliza fundamentos para os campos de IndicadorFundamentalista."""
    try:
        info = yf.Ticker(_yahoo_symbol(ticker)).info
    except Exception:
        return None
    if not info:
        return None

    roe = info.get("returnOnEquity")
    dy = info.get("dividendYield")
    return {
        "lpa": info.get("trailingEps"),
        "vpa": info.get("bookValue"),
        "p_l": info.get("trailingPE"),
        "roe": float(roe) if roe is not None else None,
        "dividend_yield": float(dy) if dy is not None else None,
    }


def get_cotacoes_historicas(ticker: str, periodo: str = "1y") -> list[dict]:
    """Retorna [{'data': date, 'preco_fechamento': float}]."""
    try:
        hist = yf.Ticker(_yahoo_symbol(ticker)).history(period=periodo)
    except Exception:
        return []
    if hist is None or hist.empty:
        return []
    saida: list[dict] = []
    for idx, row in hist.iterrows():
        saida.append({
            "data": idx.date(),
            "preco_fechamento": float(row["Close"]),
        })
    return saida
