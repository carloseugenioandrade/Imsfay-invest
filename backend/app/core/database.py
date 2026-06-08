from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _normalizar_url(url: str) -> str:
    """Garante o driver psycopg v3 para URLs Postgres (Neon manda 'postgresql://')."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):  # formato antigo de alguns provedores
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = _normalizar_url(settings.database_url)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def garantir_colunas_usuario() -> None:
    """Adiciona a coluna `usuario_id` às tabelas por-usuário se ela ainda não existir.

    `Base.metadata.create_all` cria tabelas ausentes, mas NÃO altera tabelas
    existentes. Em produção (Postgres) as tabelas já existem sem `usuario_id`,
    então fazemos um ALTER idempotente aqui. Funciona em Postgres e SQLite.
    """
    from sqlalchemy import inspect, text

    tabelas = ["transacoes", "proventos_recebidos", "gastos_financeiros", "perfil_financeiro"]
    insp = inspect(engine)
    with engine.begin() as conn:
        for tabela in tabelas:
            if not insp.has_table(tabela):
                continue
            colunas = {c["name"] for c in insp.get_columns(tabela)}
            if "usuario_id" not in colunas:
                conn.execute(text(f"ALTER TABLE {tabela} ADD COLUMN usuario_id INTEGER"))
