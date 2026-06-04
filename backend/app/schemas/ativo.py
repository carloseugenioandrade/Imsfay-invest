from pydantic import BaseModel, ConfigDict


class AtivoBase(BaseModel):
    ticker: str
    nome: str
    tipo: str  # Acao, FII, ETF, Stock, REIT, Cripto
    setor: str | None = None
    subsetor: str | None = None


class AtivoCreate(AtivoBase):
    pass


class AtivoUpdate(BaseModel):
    nome: str | None = None
    tipo: str | None = None
    setor: str | None = None
    subsetor: str | None = None


class AtivoOut(AtivoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
