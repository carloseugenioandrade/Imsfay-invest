"""Dividendos Inteligentes: previsão preditiva de meses de provento.

Abordagem: estima a probabilidade de pagamento em cada mês a partir da
frequência histórica (nº de anos em que houve provento naquele mês ÷ nº total
de anos observados). É um estimador de sazonalidade simples e explicável.
"""

from __future__ import annotations

from datetime import date


def prever_meses_provento(historico_datas: list[date]) -> dict[int, float]:
    """Retorna {mes: probabilidade(0..1)} para os 12 meses do ano."""
    probabilidades = {m: 0.0 for m in range(1, 13)}
    if not historico_datas:
        return probabilidades

    anos = {d.year for d in historico_datas}
    total_anos = len(anos)
    if total_anos == 0:
        return probabilidades

    # Conjunto de (ano, mês) para não contar dois proventos do mesmo mês em dobro.
    anos_por_mes: dict[int, set[int]] = {m: set() for m in range(1, 13)}
    for d in historico_datas:
        anos_por_mes[d.month].add(d.year)

    for mes, anos_com_provento in anos_por_mes.items():
        probabilidades[mes] = round(len(anos_com_provento) / total_anos, 3)
    return probabilidades
