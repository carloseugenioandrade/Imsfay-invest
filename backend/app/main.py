import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.database import Base, engine

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Importa os modelos para registrá-los no metadata e cria as tabelas.
    import app.models  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas verificadas/criadas com sucesso.")
    except Exception as exc:  # banco indisponível não deve derrubar a API
        logger.warning("Banco indisponível no startup (%s). Tabelas não criadas.", exc)

    if settings.enable_scheduler:
        try:
            from app.tasks.scheduler import iniciar_scheduler

            iniciar_scheduler()
        except Exception as exc:
            logger.warning("Falha ao iniciar o scheduler (%s).", exc)

    yield

    if settings.enable_scheduler:
        try:
            from app.tasks.scheduler import parar_scheduler

            parar_scheduler()
        except Exception:
            pass


app = FastAPI(
    title="Imsfay Invest API",
    description="Cockpit do Investidor de Longo Prazo — API de gestão, valuation e fiscal.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    # Aceita qualquer deploy do site no Vercel (produção e previews) sem configuração manual.
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    return {"app": "Imsfay Invest", "status": "ok", "docs": "/docs"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
