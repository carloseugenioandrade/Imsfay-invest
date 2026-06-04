"""Agendamentos (cronjobs) do sistema.

Cronjobs requeridos:
- Task_Atualizar_Cotacoes: seg-sex 18h00 (pós-fechamento) via Brapi/Yahoo.
- Task_Atualizar_Fundamentalista: domingos, recalcular rankings Graham/Bazin.

TODO: configurar APScheduler (ou Celery beat) e registrar os jobs.
"""

from __future__ import annotations


def atualizar_cotacoes() -> None:
    raise NotImplementedError("Task de atualização de cotações ainda não implementada.")


def atualizar_fundamentalista() -> None:
    raise NotImplementedError("Task de atualização fundamentalista ainda não implementada.")
