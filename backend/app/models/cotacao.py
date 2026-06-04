from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CotacaoHistorica(Base):
    __tablename__ = "cotacoes_historicas"

    id: Mapped[int] = mapped_column(primary_key=True)
    ativo_id: Mapped[int] = mapped_column(ForeignKey("ativos.id", ondelete="CASCADE"), index=True)
    data: Mapped[date] = mapped_column(Date, index=True)
    preco_fechamento: Mapped[float] = mapped_column(Numeric(18, 4))

    ativo = relationship("Ativo", back_populates="cotacoes")
