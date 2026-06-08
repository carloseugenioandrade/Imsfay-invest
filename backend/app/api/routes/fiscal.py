from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Usuario
from app.services import fiscal as fiscal_service

router = APIRouter(prefix="/fiscal", tags=["Fiscal"])


@router.get("/isentometro")
def isentometro(
    ano: int = Query(default_factory=lambda: date.today().year),
    mes: int = Query(default_factory=lambda: date.today().month, ge=1, le=12),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return fiscal_service.isentometro(db, ano, mes, usuario.id)


@router.get("/relatorio-ir")
def relatorio_ir(
    ano: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return fiscal_service.relatorio_ir(db, ano, usuario.id)
