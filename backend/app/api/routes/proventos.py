from fastapi import APIRouter

router = APIRouter(prefix="/proventos", tags=["Proventos"])


@router.get("")
async def listar_proventos():
    # TODO: listar proventos recebidos
    return {"detail": "stub", "items": []}


@router.get("/agenda-preditiva")
async def agenda_preditiva():
    # TODO: previsão de meses de provento (Dividendos Inteligentes / IA)
    return {"detail": "stub", "items": []}
