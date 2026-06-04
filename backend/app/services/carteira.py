"""Construção de posições e consolidação de patrimônio.

Calcula preço médio ponderado (por COMPRA), quantidade líquida, valor investido
e valor atual (última cotação), além de agregações por classe e setor.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ativo, CotacaoHistorica, Transacao


def _ultima_cotacao(db: Session, ativo_id: int) -> float | None:
    cot = db.scalar(
        select(CotacaoHistorica)
        .where(CotacaoHistorica.ativo_id == ativo_id)
        .order_by(CotacaoHistorica.data.desc())
    )
    return float(cot.preco_fechamento) if cot else None


def build_posicoes(db: Session) -> list[dict]:
    """Retorna a posição consolidada de cada ativo com transações."""
    posicoes: list[dict] = []
    ativos = db.scalars(select(Ativo)).all()

    for ativo in ativos:
        transacoes = db.scalars(
            select(Transacao)
            .where(Transacao.ativo_id == ativo.id)
            .order_by(Transacao.data_operacao)
        ).all()
        if not transacoes:
            continue

        quantidade = 0.0
        custo_total = 0.0  # custo da posição vigente (para preço médio)
        for t in transacoes:
            qtd = float(t.quantidade)
            preco = float(t.preco_unitario)
            taxas = float(t.taxas_corretagem or 0)
            if t.tipo_operacao == "COMPRA":
                custo_total += qtd * preco + taxas
                quantidade += qtd
            else:  # VENDA: reduz a posição pelo preço médio atual
                preco_medio = custo_total / quantidade if quantidade else 0.0
                custo_total -= preco_medio * qtd
                quantidade -= qtd

        if quantidade <= 0:
            continue

        preco_medio = custo_total / quantidade if quantidade else 0.0
        preco_atual = _ultima_cotacao(db, ativo.id)
        valor_investido = preco_medio * quantidade
        valor_atual = (preco_atual * quantidade) if preco_atual is not None else valor_investido
        lucro = valor_atual - valor_investido
        rent_pct = (lucro / valor_investido * 100) if valor_investido else 0.0

        posicoes.append({
            "ativo_id": ativo.id,
            "ticker": ativo.ticker,
            "nome": ativo.nome,
            "tipo": ativo.tipo,
            "setor": ativo.setor,
            "quantidade": round(quantidade, 8),
            "preco_medio": round(preco_medio, 4),
            "preco_atual": round(preco_atual, 4) if preco_atual is not None else None,
            "valor_investido": round(valor_investido, 2),
            "valor_atual": round(valor_atual, 2),
            "lucro": round(lucro, 2),
            "rentabilidade_pct": round(rent_pct, 2),
        })

    return posicoes


def resumo_carteira(db: Session) -> dict:
    posicoes = build_posicoes(db)
    valor_atual = sum(p["valor_atual"] for p in posicoes)
    valor_investido = sum(p["valor_investido"] for p in posicoes)
    lucro = valor_atual - valor_investido

    por_classe: dict[str, float] = defaultdict(float)
    por_setor: dict[str, float] = defaultdict(float)
    for p in posicoes:
        por_classe[p["tipo"]] += p["valor_atual"]
        por_setor[p["setor"] or "Sem setor"] += p["valor_atual"]

    return {
        "valor_atual": round(valor_atual, 2),
        "valor_investido": round(valor_investido, 2),
        "lucro": round(lucro, 2),
        "rentabilidade_pct": round((lucro / valor_investido * 100) if valor_investido else 0.0, 2),
        "quantidade_ativos": len(posicoes),
        "alocacao_por_classe": [{"nome": k, "valor": round(v, 2)} for k, v in por_classe.items()],
        "alocacao_por_setor": [{"nome": k, "valor": round(v, 2)} for k, v in por_setor.items()],
        "posicoes": posicoes,
    }


def _fator_cdi_por_data(inicio: date, fim: date) -> dict[date, float] | None:
    """Mapa {data: fator acumulado do CDI} desde `inicio`. None se indisponível."""
    from app.integrations import bcb

    serie = bcb.get_serie_por_nome(
        "CDI",
        data_inicial=inicio.strftime("%d/%m/%Y"),
        data_final=fim.strftime("%d/%m/%Y"),
    )
    if not serie:
        return None
    fator = 1.0
    mapa: dict[date, float] = {}
    for ponto in serie:
        fator *= 1 + ponto["valor"] / 100
        mapa[ponto["data"]] = fator
    return mapa


def _fator_ate(mapa: dict[date, float], dia: date) -> float:
    """Último fator acumulado conhecido até `dia` (1.0 se anterior à série)."""
    melhor = 1.0
    for d, f in mapa.items():
        if d <= dia:
            melhor = f
        else:
            break
    return melhor


def evolucao_patrimonial(db: Session, benchmark_cdi: bool = False) -> list[dict]:
    """Série temporal de patrimônio vs total investido.

    Eixo = datas distintas de cotação. Para cada data: soma, por ativo, da
    quantidade detida (transações até a data) × último preço conhecido até ali
    (carry-forward). `investido` = custo acumulado das compras líquidas até a data.
    Se `benchmark_cdi`, adiciona `cdi` = aportes corrigidos pelo CDI acumulado.
    """
    datas: list[date] = list(
        db.scalars(
            select(CotacaoHistorica.data).distinct().order_by(CotacaoHistorica.data)
        ).all()
    )
    if not datas:
        return []

    ativos = db.scalars(select(Ativo)).all()

    # Pré-carrega cotações e transações por ativo.
    cotacoes_por_ativo: dict[int, list[tuple[date, float]]] = {}
    transacoes_por_ativo: dict[int, list[Transacao]] = {}
    for ativo in ativos:
        cotacoes_por_ativo[ativo.id] = [
            (c.data, float(c.preco_fechamento))
            for c in db.scalars(
                select(CotacaoHistorica)
                .where(CotacaoHistorica.ativo_id == ativo.id)
                .order_by(CotacaoHistorica.data)
            ).all()
        ]
        transacoes_por_ativo[ativo.id] = db.scalars(
            select(Transacao)
            .where(Transacao.ativo_id == ativo.id)
            .order_by(Transacao.data_operacao)
        ).all()

    def preco_ate(ativo_id: int, dia: date) -> float | None:
        preco = None
        for d, p in cotacoes_por_ativo.get(ativo_id, []):
            if d <= dia:
                preco = p
            else:
                break
        return preco

    serie: list[dict] = []
    for dia in datas:
        patrimonio = 0.0
        investido = 0.0
        for ativo in ativos:
            quantidade = 0.0
            custo = 0.0
            for t in transacoes_por_ativo[ativo.id]:
                if t.data_operacao > dia:
                    break
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
            if quantidade <= 0:
                continue
            preco_dia = preco_ate(ativo.id, dia)
            investido += custo
            patrimonio += (preco_dia * quantidade) if preco_dia is not None else custo

        serie.append({
            "data": dia.isoformat(),
            "patrimonio": round(patrimonio, 2),
            "investido": round(investido, 2),
        })

    if benchmark_cdi and serie:
        mapa = _fator_cdi_por_data(datas[0], datas[-1])
        if mapa:
            # Aportes (COMPRA) como depósitos corrigidos pelo CDI até cada data.
            aportes: list[tuple[date, float]] = []
            for ativo in ativos:
                for t in transacoes_por_ativo[ativo.id]:
                    if t.tipo_operacao == "COMPRA":
                        valor = float(t.quantidade) * float(t.preco_unitario) + float(t.taxas_corretagem or 0)
                        aportes.append((t.data_operacao, valor))
            for ponto in serie:
                dia = date.fromisoformat(ponto["data"])
                fator_dia = _fator_ate(mapa, dia)
                total = 0.0
                for data_aporte, valor in aportes:
                    if data_aporte <= dia:
                        fator_aporte = _fator_ate(mapa, data_aporte)
                        total += valor * (fator_dia / fator_aporte)
                ponto["cdi"] = round(total, 2)

    return serie
