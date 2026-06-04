from fastapi import APIRouter

from app.services.valuation import preco_justo_graham, preco_teto_bazin, upside

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
async def ranking():
    # TODO: ranking de Upside (Graham) e abaixo do teto (Bazin) a partir do banco
    return {"detail": "stub", "items": []}
