from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    nome: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # Nulo quando a conta é apenas via Google (sem senha local).
    senha_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # 'sub' do Google quando a conta foi vinculada ao Google.
    google_sub: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    email_verificado: Mapped[bool] = mapped_column(Boolean, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
