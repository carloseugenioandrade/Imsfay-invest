from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations import bcb
from app.models import Ativo
from app.services.market import (
    importar_historico,
    sincronizar_cotacoes,
    sincronizar_fundamentos,
)

router = APIRouter(prefix="/market", tags=["Mercado"])


@router.post("/sync/cotacoes")
def sync_cotacoes(db: Session = Depends(get_db)):
    """Atualiza a cotação do dia de todos os ativos (Brapi)."""
    return sincronizar_cotacoes(db)


@router.post("/sync/fundamentos")
def sync_fundamentos(db: Session = Depends(get_db)):
    """Atualiza indicadores fundamentalistas de todos os ativos (Yahoo)."""
    return sincronizar_fundamentos(db)


@router.post("/sync/historico/{ativo_id}")
def sync_historico(
    ativo_id: int,
    periodo: str = Query("1y", description="Período yfinance: 1mo, 6mo, 1y, 5y, max"),
    db: Session = Depends(get_db),
):
    ativo = db.get(Ativo, ativo_id)
    if ativo is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    inseridos = importar_historico(db, ativo, periodo)
    return {"ticker": ativo.ticker, "inseridos": inseridos}


@router.get("/indicadores-macro")
def indicadores_macro(
    serie: str = Query("CDI", description="CDI, IPCA ou SELIC"),
    data_inicial: str | None = Query(None, description="dd/MM/yyyy"),
    data_final: str | None = Query(None, description="dd/MM/yyyy"),
):
    """Séries do Banco Central (SGS)."""
    dados = bcb.get_serie_por_nome(serie, data_inicial=data_inicial, data_final=data_final)
    return {"serie": serie.upper(), "items": dados}
