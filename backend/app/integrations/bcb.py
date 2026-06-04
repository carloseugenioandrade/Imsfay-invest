"""Cliente Banco Central (SGS - Sistema Gerenciador de Séries Temporais).

Séries úteis: 12 (CDI diário), 433 (IPCA mensal), 11 (Selic diária).
API pública: https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados

TODO: implementar requisições HTTP e parsing das séries.
"""

from __future__ import annotations

BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs"

SERIES = {"CDI": 12, "IPCA": 433, "SELIC": 11}


async def get_serie(codigo: int, data_inicial: str | None = None, data_final: str | None = None) -> list[dict]:
    raise NotImplementedError("Integração BCB (SGS) ainda não implementada.")
