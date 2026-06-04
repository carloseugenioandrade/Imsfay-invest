from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class IndicadorFundamentalista(Base):
    __tablename__ = "indicadores_fundamentalistas"

    id: Mapped[int] = mapped_column(primary_key=True)
    ativo_id: Mapped[int] = mapped_column(ForeignKey("ativos.id", ondelete="CASCADE"), index=True)
    vpa: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    lpa: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    p_l: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    roe: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    dividend_yield: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    ultima_atualizacao: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ativo = relationship("Ativo", back_populates="indicadores")
