"""Valuation clássico: Preço Justo (Graham) e Preço Teto (Bazin).

TODO: implementar leitura de `IndicadorFundamentalista` e cálculo do ranking.
"""

import math


def preco_justo_graham(lpa: float, vpa: float) -> float | None:
    if lpa <= 0 or vpa <= 0:
        return None
    return math.sqrt(22.5 * lpa * vpa)


def preco_teto_bazin(dividendos_medios_5_anos: float, yield_minimo: float = 0.06) -> float | None:
    if dividendos_medios_5_anos <= 0:
        return None
    return dividendos_medios_5_anos / yield_minimo


def upside(preco_referencia: float, preco_atual: float) -> float | None:
    if preco_atual <= 0:
        return None
    return ((preco_referencia / preco_atual) - 1) * 100
