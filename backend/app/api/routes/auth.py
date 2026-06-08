from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    criar_token,
    get_current_user,
    hash_senha,
    verificar_id_token_google,
    verificar_senha,
)
from app.models import Usuario
from app.schemas.auth import GoogleIn, LoginIn, RegisterIn, TokenOut, UsuarioOut

router = APIRouter(prefix="/auth", tags=["Autenticação"])


def _resposta_token(usuario: Usuario) -> TokenOut:
    return TokenOut(access_token=criar_token(usuario.id), usuario=UsuarioOut.model_validate(usuario))


@router.post("/register", response_model=TokenOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    email = payload.email.lower()
    if db.scalar(select(Usuario).where(Usuario.email == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este e-mail já está cadastrado.")
    usuario = Usuario(
        email=email,
        nome=payload.nome,
        senha_hash=hash_senha(payload.senha),
        email_verificado=False,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return _resposta_token(usuario)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.email == payload.email.lower()))
    if usuario is None or not usuario.senha_hash or not verificar_senha(payload.senha, usuario.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha inválidos.")
    return _resposta_token(usuario)


@router.post("/google", response_model=TokenOut)
def login_google(payload: GoogleIn, db: Session = Depends(get_db)):
    info = verificar_id_token_google(payload.credential)
    if not info.get("email"):
        raise HTTPException(status_code=401, detail="Não foi possível obter o e-mail do Google.")

    usuario = db.scalar(select(Usuario).where(Usuario.email == info["email"]))
    if usuario is None:
        usuario = Usuario(
            email=info["email"],
            nome=info.get("nome"),
            google_sub=info.get("sub"),
            avatar_url=info.get("avatar"),
            email_verificado=True,
        )
        db.add(usuario)
    else:
        # Vincula a conta existente ao Google (caso tenha sido criada por e-mail).
        usuario.google_sub = usuario.google_sub or info.get("sub")
        usuario.avatar_url = usuario.avatar_url or info.get("avatar")
        usuario.email_verificado = True
    db.commit()
    db.refresh(usuario)
    return _resposta_token(usuario)


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario
