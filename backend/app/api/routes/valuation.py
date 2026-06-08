from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Ativo, CotacaoHistorica, IndicadorFundamentalista, Transacao, Usuario
from app.services.valuation import preco_justo_graham, preco_teto_bazin, upside

BAZIN_YIELD_MINIMO = 0.06

router = APIRouter(prefix="/valuation", tags=["Valuation"])


@router.get("/graham")
async def graham(lpa: float, vpa: float, preco_atual: float):
    justo = preco_justo_graham(lpa, vpa)
    return {
        "preco_justo": justo,
        "upside_pct": upside(justo, preco_atual) if justo is not None else None,
    }


@router.get("/bazin")
async def bazin(dividendos_medios_5_anos: float, preco_atual: float):
    teto = preco_teto_bazin(dividendos_medios_5_anos)
    return {
        "preco_teto": teto,
        "abaixo_do_teto": (preco_atual <= teto) if teto is not None else None,
    }


@router.get("/ranking")
def ranking(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    """Ranking de Upside (Graham) dos ativos do usuário + última cotação do banco."""
    itens = []
    ativo_ids = set(
        db.scalars(
            select(Transacao.ativo_id).where(Transacao.usuario_id == usuario.id).distinct()
        ).all()
    )
    ativos = [a for a in db.scalars(select(Ativo)).all() if a.id in ativo_ids]
    for ativo in ativos:
        ind = db.scalar(
            select(IndicadorFundamentalista)
            .where(IndicadorFundamentalista.ativo_id == ativo.id)
            .order_by(IndicadorFundamentalista.ultima_atualizacao.desc())
        )
        cotacao = db.scalar(
            select(CotacaoHistorica)
            .where(CotacaoHistorica.ativo_id == ativo.id)
            .order_by(CotacaoHistorica.data.desc())
        )
        if ind is None or cotacao is None:
            continue
        preco_atual = float(cotacao.preco_fechamento)

        justo = (
            preco_justo_graham(float(ind.lpa), float(ind.vpa))
            if ind.lpa is not None and ind.vpa is not None
            else None
        )

        # Bazin: estima o provento anual via dividend_yield × preço atual.
        teto = None
        abaixo_teto = None
        if ind.dividend_yield is not None and ind.dividend_yield > 0:
            provento_anual = float(ind.dividend_yield) * preco_atual
            teto = preco_teto_bazin(provento_anual, BAZIN_YIELD_MINIMO)
            if teto is not None:
                abaixo_teto = preco_atual <= teto

        if justo is None and teto is None:
            continue

        itens.append({
            "ticker": ativo.ticker,
            "preco_atual": round(preco_atual, 2),
            "preco_justo": round(justo, 2) if justo is not None else None,
            "upside_pct": round(upside(justo, preco_atual) or 0, 2) if justo is not None else None,
            "preco_teto": round(teto, 2) if teto is not None else None,
            "abaixo_teto": abaixo_teto,
        })
    itens.sort(key=lambda x: (x["upside_pct"] is not None, x["upside_pct"] or -999), reverse=True)
    return {"items": itens}
