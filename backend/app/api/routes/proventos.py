from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Ativo, ProventoRecebido
from app.schemas import ProventoCreate, ProventoOut
from app.services.dividendos import agenda_preditiva as _agenda_preditiva
from app.services.dividendos import resumo_proventos as _resumo_proventos

router = APIRouter(prefix="/proventos", tags=["Proventos"])


@router.get("", response_model=list[ProventoOut])
def listar_proventos(ativo_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(ProventoRecebido).order_by(ProventoRecebido.data_pagamento.desc())
    if ativo_id is not None:
        stmt = stmt.where(ProventoRecebido.ativo_id == ativo_id)
    return db.scalars(stmt).all()


@router.post("", response_model=ProventoOut, status_code=201)
def criar_provento(payload: ProventoCreate, db: Session = Depends(get_db)):
    if db.get(Ativo, payload.ativo_id) is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    provento = ProventoRecebido(**payload.model_dump())
    db.add(provento)
    db.commit()
    db.refresh(provento)
    return provento


@router.get("/resumo")
def resumo(db: Session = Depends(get_db)):
    return _resumo_proventos(db)


@router.get("/agenda-preditiva")
def agenda_preditiva(db: Session = Depends(get_db)):
    return _agenda_preditiva(db)
