from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.integrations.importador_b3 import parse_extrato_pdf, parse_extrato_xlsx
from app.models import Ativo, Transacao
from app.schemas import TransacaoCreate, TransacaoOut

router = APIRouter(prefix="/transacoes", tags=["Transações"])


@router.get("", response_model=list[TransacaoOut])
def listar_transacoes(ativo_id: int | None = None, db: Session = Depends(get_db)):
    stmt = select(Transacao).order_by(Transacao.data_operacao.desc())
    if ativo_id is not None:
        stmt = stmt.where(Transacao.ativo_id == ativo_id)
    return db.scalars(stmt).all()


@router.post("", response_model=TransacaoOut, status_code=201)
def criar_transacao(payload: TransacaoCreate, db: Session = Depends(get_db)):
    if db.get(Ativo, payload.ativo_id) is None:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    transacao = Transacao(**payload.model_dump())
    db.add(transacao)
    db.commit()
    db.refresh(transacao)
    return transacao


@router.delete("/{transacao_id}", status_code=204)
def remover_transacao(transacao_id: int, db: Session = Depends(get_db)):
    transacao = db.get(Transacao, transacao_id)
    if transacao is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    db.delete(transacao)
    db.commit()


@router.post("/importar")
async def importar_extrato(file: UploadFile, db: Session = Depends(get_db)):
    """Importa um extrato XLSX ou PDF da B3/corretora, criando ativos ausentes
    e deduplicando transações idênticas."""
    nome = (file.filename or "").lower()
    if nome.endswith((".xlsx", ".xls")):
        formato = "xlsx"
    elif nome.endswith(".pdf"):
        formato = "pdf"
    else:
        raise HTTPException(status_code=400, detail="Envie um arquivo .xlsx ou .pdf da B3.")

    conteudo = await file.read()
    try:
        if formato == "pdf":
            linhas = parse_extrato_pdf(conteudo)
        else:
            linhas = parse_extrato_xlsx(conteudo)
    except RuntimeError as exc:  # dependência de PDF ausente
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # arquivo inválido/corrompido
        raise HTTPException(status_code=422, detail=f"Falha ao ler o {formato.upper()}: {exc}") from exc

    if not linhas:
        raise HTTPException(status_code=422, detail="Nenhuma transação reconhecida no arquivo.")

    inseridas = 0
    duplicadas = 0
    ativos_criados = 0
    cache: dict[str, Ativo] = {}

    for linha in linhas:
        ticker = linha["ticker"]
        ativo = cache.get(ticker)
        if ativo is None:
            ativo = db.scalar(select(Ativo).where(Ativo.ticker == ticker))
            if ativo is None:
                ativo = Ativo(ticker=ticker, nome=ticker, tipo=linha.get("tipo_ativo") or "Acao")
                db.add(ativo)
                db.flush()
                ativos_criados += 1
            cache[ticker] = ativo

        existente = db.scalar(
            select(Transacao).where(
                Transacao.ativo_id == ativo.id,
                Transacao.tipo_operacao == linha["tipo_operacao"],
                Transacao.data_operacao == linha["data_operacao"],
                Transacao.quantidade == linha["quantidade"],
                Transacao.preco_unitario == linha["preco_unitario"],
            )
        )
        if existente:
            duplicadas += 1
            continue

        db.add(Transacao(
            ativo_id=ativo.id,
            tipo_operacao=linha["tipo_operacao"],
            data_operacao=linha["data_operacao"],
            quantidade=linha["quantidade"],
            preco_unitario=linha["preco_unitario"],
            taxas_corretagem=0,
        ))
        inseridas += 1

    db.commit()
    return {
        "arquivo": file.filename,
        "linhas_reconhecidas": len(linhas),
        "inseridas": inseridas,
        "duplicadas": duplicadas,
        "ativos_criados": ativos_criados,
    }
