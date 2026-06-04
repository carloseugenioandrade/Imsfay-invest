"""Análise de proventos: evolução mensal, Yield on Cost e agenda preditiva."""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ativo, ProventoRecebido, Transacao
from app.services.dividendos_ia import prever_meses_provento

MESES_LABEL = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def _custo_total_investido(db: Session) -> float:
    """Custo das compras líquidas vigentes (base do Yield on Cost)."""
    total = 0.0
    for ativo in db.scalars(select(Ativo)).all():
        quantidade = 0.0
        custo = 0.0
        transacoes = db.scalars(
            select(Transacao)
            .where(Transacao.ativo_id == ativo.id)
            .order_by(Transacao.data_operacao)
        ).all()
        for t in transacoes:
            qtd = float(t.quantidade)
            preco = float(t.preco_unitario)
            taxas = float(t.taxas_corretagem or 0)
            if t.tipo_operacao == "COMPRA":
                custo += qtd * preco + taxas
                quantidade += qtd
            else:
                pm = custo / quantidade if quantidade else 0.0
                custo -= pm * qtd
                quantidade -= qtd
        if quantidade > 0:
            total += custo
    return total


def resumo_proventos(db: Session) -> dict:
    proventos = db.scalars(select(ProventoRecebido)).all()
    total = sum(float(p.valor_liquido) for p in proventos)

    por_mes: dict[str, float] = defaultdict(float)
    por_ano: dict[int, float] = defaultdict(float)
    for p in proventos:
        chave = f"{p.data_pagamento.year}-{p.data_pagamento.month:02d}"
        por_mes[chave] += float(p.valor_liquido)
        por_ano[p.data_pagamento.year] += float(p.valor_liquido)

    custo = _custo_total_investido(db)
    yield_on_cost = (total / custo * 100) if custo else 0.0

    evolucao = [
        {"mes": k, "valor": round(v, 2)} for k, v in sorted(por_mes.items())
    ]

    return {
        "total_recebido": round(total, 2),
        "yield_on_cost_pct": round(yield_on_cost, 2),
        "custo_base": round(custo, 2),
        "evolucao_mensal": evolucao,
        "por_ano": [{"ano": a, "valor": round(v, 2)} for a, v in sorted(por_ano.items())],
    }


def agenda_preditiva(db: Session) -> dict:
    """Probabilidade de provento por mês, por ativo, e agregada na carteira."""
    itens: list[dict] = []
    agregada = {m: 0.0 for m in range(1, 13)}
    n_ativos = 0

    for ativo in db.scalars(select(Ativo).order_by(Ativo.ticker)).all():
        datas = list(db.scalars(
            select(ProventoRecebido.data_pagamento).where(ProventoRecebido.ativo_id == ativo.id)
        ).all())
        if not datas:
            continue
        prob = prever_meses_provento(datas)
        n_ativos += 1
        for m in range(1, 13):
            agregada[m] += prob[m]
        itens.append({
            "ticker": ativo.ticker,
            "meses": [
                {"mes": MESES_LABEL[m - 1], "probabilidade": prob[m]} for m in range(1, 13)
            ],
        })

    carteira = [
        {
            "mes": MESES_LABEL[m - 1],
            "probabilidade": round(agregada[m] / n_ativos, 3) if n_ativos else 0.0,
        }
        for m in range(1, 13)
    ]
    return {"carteira": carteira, "por_ativo": itens}
