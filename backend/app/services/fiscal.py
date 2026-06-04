"""Módulo Fiscal: Isentômetro e auxílio ao IR.

TODO:
- Isentômetro: somar alienações (VENDA) do mês corrente e comparar com teto
  de isenção (ex.: R$ 20.000 em ações). Retornar status verde/amarelo/vermelho.
- Gerador de relatório IR: posição em 31/12 (ano anterior e vigente) com CNPJ
  e preços médios, no formato da ficha "Bens e Direitos".
"""

from __future__ import annotations

TETO_ISENCAO_ACOES = 20000.0


def isentometro_mes(total_vendas_mes: float, teto: float = TETO_ISENCAO_ACOES) -> dict:
    raise NotImplementedError("Isentômetro ainda não implementado.")


def gerar_relatorio_ir(ano: int) -> dict:
    raise NotImplementedError("Gerador de relatório de IR ainda não implementado.")
