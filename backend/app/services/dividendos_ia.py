"""Dividendos Inteligentes: previsão preditiva de meses de provento.

TODO:
- Isolar `data_com` históricas (últimos ~7 anos) por ativo.
- Agrupar por mês e calcular distribuição probabilística de anúncio.
- Treinar classificador simples (scikit-learn) e gerar agenda preditiva.
"""

from __future__ import annotations


def prever_meses_provento(historico_data_com) -> dict[int, float]:
    """Retorna {mes: probabilidade} para os 12 meses do ano."""
    raise NotImplementedError("Previsão de dividendos ainda não implementada.")
