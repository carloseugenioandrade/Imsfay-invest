from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ProventoBase(BaseModel):
    ativo_id: int
    data_pagamento: date
    data_com: date | None = None
    tipo_provento: str = Field(pattern="^(Dividendo|JCP)$")
    valor_liquido: float = Field(ge=0)


class ProventoCreate(ProventoBase):
    pass


class ProventoOut(ProventoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
