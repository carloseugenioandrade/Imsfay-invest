from fastapi import APIRouter

router = APIRouter(prefix="/carteira", tags=["Carteira"])


@router.get("/resumo")
async def resumo():
    # TODO: consolidação de patrimônio por classe/setor/moeda
    return {"detail": "stub"}


@router.get("/rentabilidade")
async def rentabilidade():
    # TODO: TWR/MWR vs Ibovespa e CDI
    return {"detail": "stub", "series": []}
