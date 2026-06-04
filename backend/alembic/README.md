# Migrations (Alembic)

A URL do banco vem de `app.core.config.settings.database_url` (resolvida em `env.py`).

## Comandos

```bash
# Gerar uma migration a partir das mudanças nos modelos
alembic revision --autogenerate -m "descricao"

# Aplicar as migrations
alembic upgrade head

# Reverter a última
alembic downgrade -1
```

> `render_as_batch=True` está habilitado para permitir `ALTER TABLE` no SQLite.
