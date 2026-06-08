"""Módulo Fiscal: Isentômetro e auxílio ao IR (renda variável).

- Isentômetro: soma alienações (VENDA) de AÇÕES no mês e compara com o teto de
  isenção de R$ 20.000; calcula lucro realizado e imposto estimado (15%).
- Relatório IR: posição em 31/12 do ano (ficha "Bens e Direitos") com preço
  médio e valor total por ativo.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Ativo, Transacao

TETO_ISENCAO_ACOES = 20000.0
ALIQUOTA_SWING_TRADE = 0.15


def _status(percentual: float) -> str:
    if percentual >= 100:
        return "vermelho"
    if percentual >= 80:
        return "amarelo"
    return "verde"


def isentometro(db: Session, ano: int, mes: int, usuario_id: int) -> dict:
    """Total de vendas de ações no mês, lucro realizado e imposto estimado.

    A isenção de R$ 20.000 vale apenas para AÇÕES (tipo 'Acao'). Lucro é apurado
    por preço médio móvel; se as vendas do mês ultrapassam o teto, o lucro deixa
    de ser isento e incide 15%.
    """
    total_vendas = 0.0
    lucro_realizado = 0.0

    ativos = db.scalars(select(Ativo).where(Ativo.tipo == "Acao")).all()
    for ativo in ativos:
        transacoes = db.scalars(
            select(Transacao)
            .where(Transacao.ativo_id == ativo.id, Transacao.usuario_id == usuario_id)
            .order_by(Transacao.data_operacao)
        ).all()
        quantidade = 0.0
        custo = 0.0
        for t in transacoes:
            qtd = float(t.quantidade)
            preco = float(t.preco_unitario)
            taxas = float(t.taxas_corretagem or 0)
            if t.tipo_operacao == "COMPRA":
                custo += qtd * preco + taxas
                quantidade += qtd
            else:
                pm = custo / quantidade if quantidade else 0.0
                if t.data_operacao.year == ano and t.data_operacao.month == mes:
                    total_vendas += qtd * preco
                    lucro_realizado += (preco - pm) * qtd - taxas
                custo -= pm * qtd
                quantidade -= qtd

    percentual = (total_vendas / TETO_ISENCAO_ACOES * 100) if TETO_ISENCAO_ACOES else 0.0
    isento = total_vendas <= TETO_ISENCAO_ACOES
    imposto = 0.0
    if not isento and lucro_realizado > 0:
        imposto = lucro_realizado * ALIQUOTA_SWING_TRADE

    return {
        "ano": ano,
        "mes": mes,
        "total_vendas": round(total_vendas, 2),
        "teto": TETO_ISENCAO_ACOES,
        "percentual_teto": round(percentual, 2),
        "isento": isento,
        "status": _status(percentual),
        "lucro_realizado": round(lucro_realizado, 2),
        "imposto_estimado": round(imposto, 2),
    }


def relatorio_ir(db: Session, ano: int, usuario_id: int) -> dict:
    """Posição em 31/12/ano por ativo (Bens e Direitos)."""
    corte = date(ano, 12, 31)
    itens: list[dict] = []
    total = 0.0

    for ativo in db.scalars(select(Ativo).order_by(Ativo.ticker)).all():
        transacoes = db.scalars(
            select(Transacao)
            .where(
                Transacao.ativo_id == ativo.id,
                Transacao.usuario_id == usuario_id,
                Transacao.data_operacao <= corte,
            )
            .order_by(Transacao.data_operacao)
        ).all()
        quantidade = 0.0
        custo = 0.0
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

        if quantidade <= 0:
            continue
        preco_medio = custo / quantidade if quantidade else 0.0
        valor = preco_medio * quantidade
        total += valor
        itens.append({
            "ticker": ativo.ticker,
            "nome": ativo.nome,
            "tipo": ativo.tipo,
            "quantidade": round(quantidade, 8),
            "preco_medio": round(preco_medio, 4),
            "valor_total": round(valor, 2),
            "discriminacao": (
                f"{int(quantidade) if quantidade.is_integer() else quantidade} x {ativo.ticker} "
                f"({ativo.nome}) — PM R$ {preco_medio:.2f}"
            ),
        })

    return {"ano": ano, "data_posicao": corte.isoformat(), "total": round(total, 2), "itens": itens}
