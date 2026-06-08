"""Autenticação: hash de senha (bcrypt), tokens JWT e verificação do Google."""

from datetime import datetime, timedelta, timezone

import bcrypt
import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import Usuario

ALGORITMO = "HS256"
GOOGLE_TOKENINFO = "https://oauth2.googleapis.com/tokeninfo"

bearer = HTTPBearer(auto_error=False)


# ===== Senha =====
def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode("utf-8")[:72], senha_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ===== JWT =====
def criar_token(usuario_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(usuario_id), "exp": expira}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITMO)


def _decodificar_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITMO])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    if cred is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    usuario_id = _decodificar_token(cred.credentials)
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")
    return usuario


# ===== Google =====
def verificar_id_token_google(id_token: str) -> dict:
    """Valida o ID token do Google e devolve {email, sub, nome, avatar}."""
    try:
        resp = httpx.get(GOOGLE_TOKENINFO, params={"id_token": id_token}, timeout=10)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Falha ao contatar o Google.") from exc

    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Token do Google inválido.")
    dados = resp.json()

    # Se um Client ID estiver configurado, exige que o token tenha sido emitido para ele.
    if settings.google_client_id and dados.get("aud") != settings.google_client_id:
        raise HTTPException(status_code=401, detail="Token do Google não pertence a este app.")
    if dados.get("email_verified") not in ("true", True):
        raise HTTPException(status_code=401, detail="E-mail do Google não verificado.")

    return {
        "email": dados.get("email", "").lower(),
        "sub": dados.get("sub"),
        "nome": dados.get("name"),
        "avatar": dados.get("picture"),
    }
