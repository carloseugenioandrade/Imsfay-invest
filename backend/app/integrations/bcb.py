"""Cliente Banco Central (SGS - Sistema Gerenciador de Séries Temporais).

Séries úteis: 12 (CDI diário), 433 (IPCA mensal), 11 (Selic diária).
API pública: https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados
"""

from __future__ import annotations

from datetime import datetime

import httpx

BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"
TIMEOUT = 12.0

SERIES = {"CDI": 12, "IPCA": 433, "SELIC": 11}


def get_serie(
    codigo: int,
    data_inicial: str | None = None,
    data_final: str | None = None,
) -> list[dict]:
    """Retorna [{'data': date, 'valor': float}] da série SGS informada.

    Datas no formato dd/MM/yyyy. Sem datas, retorna a série completa (use com
    parcimônia para séries diárias longas).
    """
    params: dict[str, str] = {"formato": "json"}
    if data_inicial:
        params["dataInicial"] = data_inicial
    if data_final:
        params["dataFinal"] = data_final

    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            resp = client.get(f"{BASE_URL}.{codigo}/dados", params=params)
            resp.raise_for_status()
            dados = resp.json()
    except (httpx.HTTPError, ValueError):
        return []

    saida: list[dict] = []
    for item in dados:
        try:
            dt = datetime.strptime(item["data"], "%d/%m/%Y").date()
            valor = float(item["valor"].replace(",", "."))
        except (KeyError, ValueError, AttributeError):
            continue
        saida.append({"data": dt, "valor": valor})
    return saida


def get_serie_por_nome(nome: str, **kwargs) -> list[dict]:
    codigo = SERIES.get(nome.upper())
    if codigo is None:
        return []
    return get_serie(codigo, **kwargs)
