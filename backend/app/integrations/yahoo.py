"""Cliente Yahoo Finance (via biblioteca `yfinance`).

Uso: dados fundamentalistas brutos (LPA, VPA, margens, dívidas) e cotações
internacionais (Stocks, REITs, Cripto).

TODO: implementar coleta com yfinance e normalização para os modelos.
"""

from __future__ import annotations


def get_fundamentos(ticker: str) -> dict:
    raise NotImplementedError("Integração Yahoo (fundamentos) ainda não implementada.")


def get_cotacoes_historicas(ticker: str, periodo: str = "1y") -> list[dict]:
    raise NotImplementedError("Integração Yahoo (histórico) ainda não implementada.")
