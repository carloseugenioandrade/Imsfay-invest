from fastapi import APIRouter

router = APIRouter(prefix="/fiscal", tags=["Fiscal"])


@router.get("/isentometro")
async def isentometro():
    # TODO: soma de vendas do mês vs teto de isenção (R$ 20.000 em ações)
    return {"detail": "stub"}


@router.get("/relatorio-ir")
async def relatorio_ir(ano: int):
    # TODO: posição 31/12 (Bens e Direitos) com CNPJ e preço médio
    return {"detail": "stub", "ano": ano}
