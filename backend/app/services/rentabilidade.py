"""Engine de carteira: preço médio, TWR/MWR e consolidação de patrimônio.

TODO:
- Calcular preço médio ponderado por transação (COMPRA).
- Implementar TWR (Time-Weighted Return) e/ou MWR.
- Comparar curva de patrimônio com Ibovespa e CDI.
- Agregar patrimônio por classe de ativo, setor e moeda.
"""

from __future__ import annotations


def preco_medio(transacoes) -> float:
    raise NotImplementedError("Cálculo de preço médio ainda não implementado.")


def time_weighted_return(serie_patrimonio, fluxos_caixa) -> float:
    raise NotImplementedError("TWR ainda não implementado.")


def consolidar_patrimonio(posicoes) -> dict:
    raise NotImplementedError("Consolidação de patrimônio ainda não implementada.")
