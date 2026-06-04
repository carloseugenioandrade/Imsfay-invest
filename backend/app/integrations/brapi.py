"""Cliente Brapi (https://brapi.dev) — cotações e proventos da B3.

Chamadas HTTP autenticadas com `settings.brapi_token` (opcional no plano free).
"""

from __future__ import annotations

from datetime import date, datetime

import httpx

from app.core.config import settings

BASE_URL = "https://brapi.dev/api"
TIMEOUT = 12.0


def _params(extra: dict | None = None) -> dict:
    params = dict(extra or {})
    if settings.brapi_token:
        params["token"] = settings.brapi_token
    return params


def get_cotacao(ticker: str) -> dict | None:
    """Retorna {'ticker', 'preco', 'data', 'nome'} ou None se indisponível."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            resp = client.get(f"{BASE_URL}/quote/{ticker}", params=_params())
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPError, ValueError):
        return None

    resultados = data.get("results") or []
    if not resultados:
        return None
    r = resultados[0]
    preco = r.get("regularMarketPrice")
    if preco is None:
        return None
    return {
        "ticker": r.get("symbol", ticker).upper(),
        "preco": float(preco),
        "data": date.today(),
        "nome": r.get("longName") or r.get("shortName"),
    }


def get_dividendos(ticker: str) -> list[dict]:
    """Lista de proventos: [{'data_pagamento', 'tipo', 'valor'}]."""
    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            resp = client.get(
                f"{BASE_URL}/quote/{ticker}",
                params=_params({"dividends": "true"}),
            )
            resp.raise_for_status()
            data = resp.json()
    except (httpx.HTTPError, ValueError):
        return []

    resultados = data.get("results") or []
    if not resultados:
        return []
    dividendos = (
        resultados[0]
        .get("dividendsData", {})
        .get("cashDividends", [])
    )
    saida: list[dict] = []
    for d in dividendos:
        pagamento = d.get("paymentDate") or d.get("lastDatePrior")
        valor = d.get("rate")
        if not pagamento or valor is None:
            continue
        try:
            dt = datetime.fromisoformat(pagamento.replace("Z", "")).date()
        except ValueError:
            continue
        saida.append({
            "data_pagamento": dt,
            "tipo": (d.get("label") or "Dividendo"),
            "valor": float(valor),
        })
    return saida
