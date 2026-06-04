from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Ativo
from app.schemas import AtivoCreate, AtivoOut, AtivoUpdate

router = APIRouter(prefix="/ativos", tags=["Ativos"])


@router.get("", response_model=list[AtivoOut])
def listar_ativos(db: Session = Depends(get_db)):
    return db.scalars(select(Ativo).order_by(Ativo.ticker)).all()


@router.get("/{ativo_id}", response_model=AtivoOut)
def obter_ativo(ativo_id: int, db: Session = Depends(get_db)):
    ativo = db.get(Ativo, ativo_id)
    if ativo is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    return ativo


@router.post("", response_model=AtivoOut, status_code=201)
def criar_ativo(payload: AtivoCreate, db: Session = Depends(get_db)):
    existente = db.scalar(select(Ativo).where(Ativo.ticker == payload.ticker.upper()))
    if existente is not None:
        raise HTTPException(status_code=409, detail="Ticker já cadastrado")
    ativo = Ativo(**payload.model_dump())
    ativo.ticker = ativo.ticker.upper()
    db.add(ativo)
    db.commit()
    db.refresh(ativo)
    return ativo


@router.patch("/{ativo_id}", response_model=AtivoOut)
def atualizar_ativo(ativo_id: int, payload: AtivoUpdate, db: Session = Depends(get_db)):
    ativo = db.get(Ativo, ativo_id)
    if ativo is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(ativo, campo, valor)
    db.commit()
    db.refresh(ativo)
    return ativo


@router.delete("/{ativo_id}", status_code=204)
def remover_ativo(ativo_id: int, db: Session = Depends(get_db)):
    ativo = db.get(Ativo, ativo_id)
    if ativo is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    db.delete(ativo)
    db.commit()
