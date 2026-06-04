from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Transacao(Base):
    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    ativo_id: Mapped[int] = mapped_column(ForeignKey("ativos.id", ondelete="CASCADE"), index=True)
    tipo_operacao: Mapped[str] = mapped_column(String(10))  # COMPRA / VENDA
    data_operacao: Mapped[date] = mapped_column(Date, index=True)
    quantidade: Mapped[float] = mapped_column(Numeric(18, 8))
    preco_unitario: Mapped[float] = mapped_column(Numeric(18, 4))
    taxas_corretagem: Mapped[float] = mapped_column(Numeric(18, 4), default=0)

    ativo = relationship("Ativo", back_populates="transacoes")
