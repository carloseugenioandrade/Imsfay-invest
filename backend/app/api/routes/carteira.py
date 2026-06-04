from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.carteira import build_posicoes, evolucao_patrimonial, resumo_carteira

router = APIRouter(prefix="/carteira", tags=["Carteira"])


@router.get("/resumo")
def resumo(db: Session = Depends(get_db)):
    return resumo_carteira(db)


@router.get("/posicoes")
def posicoes(db: Session = Depends(get_db)):
    return {"items": build_posicoes(db)}


@router.get("/evolucao")
def evolucao(benchmark_cdi: bool = False, db: Session = Depends(get_db)):
    return {"items": evolucao_patrimonial(db, benchmark_cdi=benchmark_cdi)}


@router.get("/rentabilidade")
async def rentabilidade():
    # TODO (Fase 4): TWR/MWR vs Ibovespa e CDI
    return {"detail": "stub", "series": []}
