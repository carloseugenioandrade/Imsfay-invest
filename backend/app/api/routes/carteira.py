from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Usuario
from app.services.carteira import build_posicoes, evolucao_patrimonial, resumo_carteira

router = APIRouter(prefix="/carteira", tags=["Carteira"])


@router.get("/resumo")
def resumo(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return resumo_carteira(db, usuario.id)


@router.get("/posicoes")
def posicoes(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    return {"items": build_posicoes(db, usuario.id)}


@router.get("/evolucao")
def evolucao(
    benchmark_cdi: bool = False,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return {"items": evolucao_patrimonial(db, usuario.id, benchmark_cdi=benchmark_cdi)}
