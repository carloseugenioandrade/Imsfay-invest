from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class TransacaoBase(BaseModel):
    ativo_id: int
    tipo_operacao: str = Field(pattern="^(COMPRA|VENDA)$")
    data_operacao: date
    quantidade: float = Field(gt=0)
    preco_unitario: float = Field(ge=0)
    taxas_corretagem: float = Field(default=0, ge=0)


class TransacaoCreate(TransacaoBase):
    pass


class TransacaoOut(TransacaoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
