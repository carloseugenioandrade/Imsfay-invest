from fastapi import APIRouter

router = APIRouter(prefix="/ativos", tags=["Ativos"])


@router.get("")
async def listar_ativos():
    # TODO: listar ativos do banco
    return {"detail": "stub", "items": []}


@router.post("", status_code=201)
async def criar_ativo():
    # TODO: criar ativo
    return {"detail": "stub"}
