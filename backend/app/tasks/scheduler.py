"""Agendamentos (cronjobs) do sistema via APScheduler.

Jobs:
- atualizar_cotacoes: seg-sex 18h00 (pós-fechamento) via Brapi.
- atualizar_fundamentalista: domingos 08h00, fundamentos via Yahoo.
"""

from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.services.market import sincronizar_cotacoes, sincronizar_fundamentos

logger = logging.getLogger("uvicorn.error")

_scheduler: BackgroundScheduler | None = None


def atualizar_cotacoes() -> None:
    db = SessionLocal()
    try:
        resultado = sincronizar_cotacoes(db)
        logger.info("Job cotações: %s atualizados, %s falhas.",
                    len(resultado["atualizados"]), len(resultado["falhas"]))
    finally:
        db.close()


def atualizar_fundamentalista() -> None:
    db = SessionLocal()
    try:
        resultado = sincronizar_fundamentos(db)
        logger.info("Job fundamentos: %s atualizados, %s falhas.",
                    len(resultado["atualizados"]), len(resultado["falhas"]))
    finally:
        db.close()


def iniciar_scheduler() -> BackgroundScheduler:
    """Cria e inicia o agendador (idempotente)."""
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(
        atualizar_cotacoes,
        trigger="cron",
        day_of_week="mon-fri",
        hour=18,
        minute=0,
        id="atualizar_cotacoes",
        replace_existing=True,
    )
    scheduler.add_job(
        atualizar_fundamentalista,
        trigger="cron",
        day_of_week="sun",
        hour=8,
        minute=0,
        id="atualizar_fundamentalista",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler iniciado (cotações 18h seg-sex; fundamentos dom 08h).")
    _scheduler = scheduler
    return scheduler


def parar_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
