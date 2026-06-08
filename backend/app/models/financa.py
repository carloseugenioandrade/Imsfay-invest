from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GastoFinanceiro(Base):
    """Lançamento do organizador financeiro pessoal (receita ou despesa)."""

    __tablename__ = "gastos_financeiros"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, nullable=True
    )
    tipo: Mapped[str] = mapped_column(String(10), index=True)  # receita / despesa
    categoria: Mapped[str] = mapped_column(String(40), index=True)
    descricao: Mapped[str | None] = mapped_column(String(160), nullable=True)
    valor: Mapped[float] = mapped_column(Numeric(18, 2))
    data: Mapped[date] = mapped_column(Date, index=True)
    recorrente: Mapped[bool] = mapped_column(Boolean, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PerfilFinanceiro(Base):
    """Perfil único do usuário (single-user): renda, perfil investidor e progresso da jornada."""

    usuario_id: Mapped[int | None] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"), index=True, unique=True, nullable=True
    )
    __tablename__ = "perfil_financeiro"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Diagnóstico financeiro
    renda_mensal: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    gasto_mensal_estimado: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    total_dividas: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    reserva_atual: Mapped[float] = mapped_column(Numeric(18, 2), default=0)
    meses_reserva_meta: Mapped[int] = mapped_column(Integer, default=6)

    # Perfil de investidor (quiz de 10 perguntas)
    perfil_investidor: Mapped[str | None] = mapped_column(String(20), nullable=True)  # Conservador/Moderado/Arrojado
    score_perfil: Mapped[int] = mapped_column(Integer, default=0)
    respostas_quiz: Mapped[str | None] = mapped_column(String(200), nullable=True)  # JSON: lista de índices

    # Progresso da trilha (JSON: lista de ids de capítulos concluídos)
    capitulos_concluidos: Mapped[str | None] = mapped_column(String(400), nullable=True)
    onboarding_completo: Mapped[bool] = mapped_column(Boolean, default=False)

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
