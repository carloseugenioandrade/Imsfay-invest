from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import GastoFinanceiro, PerfilFinanceiro


def get_or_create_perfil(db: Session, usuario_id: int) -> PerfilFinanceiro:
    perfil = db.scalar(select(PerfilFinanceiro).where(PerfilFinanceiro.usuario_id == usuario_id))
    if perfil is None:
        perfil = PerfilFinanceiro(usuario_id=usuario_id)
        db.add(perfil)
        db.commit()
        db.refresh(perfil)
    return perfil


def _inicio_mes(d: date) -> date:
    return d.replace(day=1)


def _add_meses(d: date, n: int) -> date:
    mes = d.month - 1 + n
    ano = d.year + mes // 12
    return date(ano, mes % 12 + 1, 1)


def resumo_financeiro(db: Session, usuario_id: int, ref: date | None = None) -> dict:
    """Resumo do mês de referência + tendência dos últimos 6 meses."""
    hoje = ref or date.today()
    ini = _inicio_mes(hoje)
    fim = _add_meses(ini, 1)

    gastos = db.scalars(
        select(GastoFinanceiro).where(
            GastoFinanceiro.usuario_id == usuario_id,
            GastoFinanceiro.data >= ini,
            GastoFinanceiro.data < fim,
        )
    ).all()

    receitas = sum(float(g.valor) for g in gastos if g.tipo == "receita")
    despesas = sum(float(g.valor) for g in gastos if g.tipo == "despesa")
    saldo = receitas - despesas
    taxa_poupanca = (saldo / receitas * 100) if receitas else 0.0

    por_categoria: dict[str, float] = defaultdict(float)
    for g in gastos:
        if g.tipo == "despesa":
            por_categoria[g.categoria] += float(g.valor)
    categorias = sorted(
        ({"categoria": k, "valor": round(v, 2)} for k, v in por_categoria.items()),
        key=lambda x: x["valor"],
        reverse=True,
    )

    # Tendência dos últimos 6 meses
    serie = []
    for i in range(5, -1, -1):
        mi = _add_meses(ini, -i)
        mf = _add_meses(mi, 1)
        ms = db.scalars(
            select(GastoFinanceiro).where(
                GastoFinanceiro.usuario_id == usuario_id,
                GastoFinanceiro.data >= mi,
                GastoFinanceiro.data < mf,
            )
        ).all()
        r = sum(float(g.valor) for g in ms if g.tipo == "receita")
        d = sum(float(g.valor) for g in ms if g.tipo == "despesa")
        serie.append(
            {
                "mes": mi.strftime("%m/%Y"),
                "receitas": round(r, 2),
                "despesas": round(d, 2),
                "saldo": round(r - d, 2),
            }
        )

    return {
        "mes_referencia": ini.strftime("%m/%Y"),
        "receitas": round(receitas, 2),
        "despesas": round(despesas, 2),
        "saldo": round(saldo, 2),
        "taxa_poupanca": round(taxa_poupanca, 1),
        "por_categoria": categorias,
        "serie_mensal": serie,
    }


def gasto_medio_mensal(db: Session, usuario_id: int, meses: int = 3) -> float:
    """Média de despesas dos últimos `meses` (ignora meses sem lançamentos)."""
    hoje = date.today()
    ini = _inicio_mes(hoje)
    totais: list[float] = []
    for i in range(meses):
        mi = _add_meses(ini, -i)
        mf = _add_meses(mi, 1)
        ms = db.scalars(
            select(GastoFinanceiro).where(
                GastoFinanceiro.usuario_id == usuario_id,
                GastoFinanceiro.data >= mi,
                GastoFinanceiro.data < mf,
                GastoFinanceiro.tipo == "despesa",
            )
        ).all()
        total = sum(float(g.valor) for g in ms)
        if total > 0:
            totais.append(total)
    if totais:
        return round(sum(totais) / len(totais), 2)
    return 0.0
