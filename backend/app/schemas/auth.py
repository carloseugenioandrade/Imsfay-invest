from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    nome: str | None = Field(default=None, max_length=120)


class LoginIn(BaseModel):
    email: EmailStr
    senha: str


class GoogleIn(BaseModel):
    credential: str  # ID token (JWT) retornado pelo Google Identity Services


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nome: str | None
    avatar_url: str | None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut
