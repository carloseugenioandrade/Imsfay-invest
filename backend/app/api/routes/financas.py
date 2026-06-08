from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import GastoFinanceiro
from app.schemas import GastoCreate, GastoOut, PerfilOut, PerfilUpdate
from app.services.financas import get_or_create_perfil, resumo_financeiro

router = APIRouter(prefix="/financas", tags=["Finanças"])


@router.get("/lancamentos", response_model=list[GastoOut])
def listar_lancamentos(tipo: str | None = None, db: Session = Depends(get_db)):
    stmt = select(GastoFinanceiro).order_by(GastoFinanceiro.data.desc(), GastoFinanceiro.id.desc())
    if tipo in ("receita", "despesa"):
        stmt = stmt.where(GastoFinanceiro.tipo == tipo)
    return db.scalars(stmt).all()


@router.post("/lancamentos", response_model=GastoOut, status_code=201)
def criar_lancamento(payload: GastoCreate, db: Session = Depends(get_db)):
    gasto = GastoFinanceiro(**payload.model_dump())
    db.add(gasto)
    db.commit()
    db.refresh(gasto)
    return gasto


@router.delete("/lancamentos/{lancamento_id}", status_code=204)
def remover_lancamento(lancamento_id: int, db: Session = Depends(get_db)):
    gasto = db.get(GastoFinanceiro, lancamento_id)
    if gasto is None:
        raise HTTPException(status_code=404, detail="Lançamento não encontrado")
    db.delete(gasto)
    db.commit()


@router.get("/resumo")
def resumo(db: Session = Depends(get_db)):
    return resumo_financeiro(db)


@router.get("/perfil", response_model=PerfilOut)
def obter_perfil(db: Session = Depends(get_db)):
    return get_or_create_perfil(db)


@router.patch("/perfil", response_model=PerfilOut)
def atualizar_perfil(payload: PerfilUpdate, db: Session = Depends(get_db)):
    perfil = get_or_create_perfil(db)
    dados = payload.model_dump(exclude_unset=True)
    for campo, valor in dados.items():
        setattr(perfil, campo, valor)
    if dados:
        perfil.onboarding_completo = True
    db.commit()
    db.refresh(perfil)
    return perfil
