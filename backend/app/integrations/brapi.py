"""Cliente Brapi (https://brapi.dev) — cotações e proventos da B3.

TODO: implementar chamadas HTTP autenticadas com `settings.brapi_token`.
"""

from __future__ import annotations

BASE_URL = "https://brapi.dev/api"


async def get_cotacao(ticker: str) -> dict:
    raise NotImplementedError("Integração Brapi (cotação) ainda não implementada.")


async def get_dividendos(ticker: str) -> list[dict]:
    raise NotImplementedError("Integração Brapi (dividendos) ainda não implementada.")
