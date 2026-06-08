from datetime import date

from pydantic import BaseModel, ConfigDict, Field


# ===== Organizador financeiro =====
class GastoBase(BaseModel):
    tipo: str = Field(pattern="^(receita|despesa)$")
    categoria: str = Field(min_length=1, max_length=40)
    descricao: str | None = Field(default=None, max_length=160)
    valor: float = Field(gt=0)
    data: date
    recorrente: bool = False


class GastoCreate(GastoBase):
    pass


class GastoOut(GastoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ===== Perfil / Jornada =====
class PerfilUpdate(BaseModel):
    renda_mensal: float | None = Field(default=None, ge=0)
    gasto_mensal_estimado: float | None = Field(default=None, ge=0)
    total_dividas: float | None = Field(default=None, ge=0)
    reserva_atual: float | None = Field(default=None, ge=0)
    meses_reserva_meta: int | None = Field(default=None, ge=1, le=24)


class QuizSubmit(BaseModel):
    # Lista de índices de alternativa (0..3) para as 10 perguntas.
    respostas: list[int] = Field(min_length=10, max_length=10)


class PerfilOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    renda_mensal: float
    gasto_mensal_estimado: float
    total_dividas: float
    reserva_atual: float
    meses_reserva_meta: int
    perfil_investidor: str | None
    score_perfil: int
    onboarding_completo: bool
