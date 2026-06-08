from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProventoRecebido(Base):
    __tablename__ = "proventos_recebidos"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, nullable=True
    )
    ativo_id: Mapped[int] = mapped_column(ForeignKey("ativos.id", ondelete="CASCADE"), index=True)
    data_pagamento: Mapped[date] = mapped_column(Date, index=True)
    data_com: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    tipo_provento: Mapped[str] = mapped_column(String(20))  # Dividendo / JCP
    valor_liquido: Mapped[float] = mapped_column(Numeric(18, 4))

    ativo = relationship("Ativo", back_populates="proventos")
