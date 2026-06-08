from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Ativo(Base):
    __tablename__ = "ativos"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticker: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    nome: Mapped[str] = mapped_column(String(120))
    tipo: Mapped[str] = mapped_column(String(20))  # Acao, FII, ETF, Stock, REIT, Cripto
    setor: Mapped[str | None] = mapped_column(String(80), nullable=True)
    subsetor: Mapped[str | None] = mapped_column(String(80), nullable=True)

    cotacoes = relationship("CotacaoHistorica", back_populates="ativo", cascade="all, delete-orphan")
    transacoes = relationship("Transacao", back_populates="ativo", cascade="all, delete-orphan")
    proventos = relationship("ProventoRecebido", back_populates="ativo", cascade="all, delete-orphan")
    indicadores = relationship("IndicadorFundamentalista", back_populates="ativo", cascade="all, delete-orphan")
