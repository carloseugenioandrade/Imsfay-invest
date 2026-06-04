"""Sincronização de dados de mercado para o banco.

Usa as integrações (Brapi, Yahoo) para popular `cotacoes_historicas` e
`indicadores_fundamentalistas`. Tolerante a falhas: um ticker que falhar não
interrompe os demais.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations import brapi, yahoo
from app.models import Ativo, CotacaoHistorica, IndicadorFundamentalista


def _upsert_cotacao(db: Session, ativo_id: int, dia: date, preco: float) -> None:
    existente = db.scalar(
        select(CotacaoHistorica).where(
            CotacaoHistorica.ativo_id == ativo_id,
            CotacaoHistorica.data == dia,
        )
    )
    if existente:
        existente.preco_fechamento = preco
    else:
        db.add(CotacaoHistorica(ativo_id=ativo_id, data=dia, preco_fechamento=preco))


def sincronizar_cotacoes(db: Session) -> dict:
    """Atualiza a cotação do dia de cada ativo via Brapi."""
    atualizados: list[str] = []
    falhas: list[str] = []
    for ativo in db.scalars(select(Ativo)).all():
        cot = brapi.get_cotacao(ativo.ticker)
        if cot is None:
            falhas.append(ativo.ticker)
            continue
        _upsert_cotacao(db, ativo.id, cot["data"], cot["preco"])
        atualizados.append(ativo.ticker)
    db.commit()
    return {"atualizados": atualizados, "falhas": falhas}


def sincronizar_fundamentos(db: Session) -> dict:
    """Atualiza/insere indicadores fundamentalistas via Yahoo."""
    atualizados: list[str] = []
    falhas: list[str] = []
    for ativo in db.scalars(select(Ativo)).all():
        fund = yahoo.get_fundamentos(ativo.ticker)
        if fund is None or all(v is None for v in fund.values()):
            falhas.append(ativo.ticker)
            continue
        ind = db.scalar(
            select(IndicadorFundamentalista).where(
                IndicadorFundamentalista.ativo_id == ativo.id
            )
        )
        if ind is None:
            ind = IndicadorFundamentalista(ativo_id=ativo.id)
            db.add(ind)
        for campo, valor in fund.items():
            if valor is not None:
                setattr(ind, campo, valor)
        atualizados.append(ativo.ticker)
    db.commit()
    return {"atualizados": atualizados, "falhas": falhas}


def importar_historico(db: Session, ativo: Ativo, periodo: str = "1y") -> int:
    """Importa cotações históricas (Yahoo) para um ativo. Retorna nº inseridos."""
    historico = yahoo.get_cotacoes_historicas(ativo.ticker, periodo)
    inseridos = 0
    for ponto in historico:
        existente = db.scalar(
            select(CotacaoHistorica).where(
                CotacaoHistorica.ativo_id == ativo.id,
                CotacaoHistorica.data == ponto["data"],
            )
        )
        if existente is None:
            db.add(CotacaoHistorica(
                ativo_id=ativo.id,
                data=ponto["data"],
                preco_fechamento=ponto["preco_fechamento"],
            ))
            inseridos += 1
    db.commit()
    return inseridos
