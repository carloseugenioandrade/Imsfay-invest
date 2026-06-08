import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Usuario
from app.schemas import QuizSubmit
from app.services.financas import get_or_create_perfil
from app.services.jornada import (
    QUIZ,
    avaliar_perfil,
    construir_trilha,
    salvar_concluidos,
    _carregar_concluidos,
)

router = APIRouter(prefix="/jornada", tags=["Jornada"])

# Capítulos de leitura que podem ser marcados como concluídos manualmente.
_CAPITULOS_LEITURA = {"comecar_investir", "consistencia"}


@router.get("")
def obter_trilha(db: Session = Depends(get_db), usuario: Usuario = Depends(get_current_user)):
    perfil = get_or_create_perfil(db, usuario.id)
    return construir_trilha(db, perfil)


@router.get("/quiz")
def obter_quiz():
    return {"perguntas": QUIZ}


@router.post("/quiz")
def enviar_quiz(
    payload: QuizSubmit,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    perfil_nome, score = avaliar_perfil(payload.respostas)
    perfil = get_or_create_perfil(db, usuario.id)
    perfil.perfil_investidor = perfil_nome
    perfil.score_perfil = score
    perfil.respostas_quiz = json.dumps(payload.respostas)
    db.commit()
    db.refresh(perfil)
    return {"perfil_investidor": perfil_nome, "score": score}


@router.post("/capitulos/{capitulo_id}/concluir")
def concluir_capitulo(
    capitulo_id: str,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if capitulo_id not in _CAPITULOS_LEITURA:
        raise HTTPException(status_code=400, detail="Este capítulo é concluído automaticamente pelos seus dados.")
    perfil = get_or_create_perfil(db, usuario.id)
    concluidos = _carregar_concluidos(perfil)
    concluidos.add(capitulo_id)
    salvar_concluidos(perfil, concluidos)
    db.commit()
    return {"ok": True, "capitulo": capitulo_id}
