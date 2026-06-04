# Plano de Execução — Imsfay Invest

Plano por fases para sair do esqueleto atual até o produto completo. Cada fase
entrega algo funcional e testável. Marque os itens conforme avançar.

---

## Fase 0 — Fundação (CONCLUÍDA: esqueleto)
- [x] Estrutura do monorepo (`backend/`, `frontend/`, `docs/`).
- [x] `docker-compose` com Postgres + Redis + backend + frontend.
- [x] Backend FastAPI: config, conexão, modelos (5 entidades), rotas stub.
- [x] Frontend React/Vite/TS + Tailwind: layout, rotas e páginas stub.
- [ ] Rodar `pip install` + `npm install` e validar `docker compose up`.

> Após `npm install`/`pip install` os erros de lint atuais (módulos não
> encontrados) desaparecem — eles existem apenas porque as dependências ainda
> não foram instaladas.

---

## Fase 1 — Persistência e CRUD básico (CONCLUÍDA)
**Objetivo:** banco vivo com dados manuais.
- [x] Banco de desenvolvimento **SQLite** (zero config); Postgres via `.env`/Docker.
- [x] Criação de tabelas no startup (`lifespan` + `create_all`, resiliente).
- [x] Schemas Pydantic (entrada/saída) para `Ativo`, `Transacao`, `Provento`.
- [x] CRUD real em `ativos`, `transacoes`, `proventos` (substituiu stubs).
- [x] Ranking de Valuation (Graham) lendo indicadores + cotação do banco.
- [x] Seed de dados de exemplo re-executável (`backend/seed.py`).
- [x] **Alembic** configurado (`alembic/`) + migration inicial autogerada.
- [x] Testes de API (pytest + TestClient): 9 testes verdes.

## Fase 2 — Ingestão de dados de mercado (CONCLUÍDA)
**Objetivo:** preencher cotações e fundamentos automaticamente.
- [x] `integrations/brapi.py`: cotações e dividendos da B3 (token via `.env`).
- [x] `integrations/yahoo.py`: fundamentos (LPA, VPA, P/L, ROE, DY) + histórico (`.SA`).
- [x] `integrations/bcb.py`: séries CDI (12), IPCA (433), Selic (11) — validado.
- [x] `services/market.py`: persiste em `cotacoes_historicas` e `indicadores_fundamentalistas`.
- [x] Rotas `/market/sync/*` e `/market/indicadores-macro`.
- [x] Botão "Sincronizar mercado" no Dashboard.
- [x] Tratamento de erros/timeout (falha de um ticker não derruba os demais).
- [x] Agendamento (APScheduler) para sync periódico — ver Fase 8.

## Fase 3 — Valuation (Graham & Bazin) (CONCLUÍDA)
**Objetivo:** rankings de margem de segurança.
- [x] `services/valuation.py` ligado aos `indicadores_fundamentalistas`.
- [x] Rota `/valuation/ranking`: Upside (Graham) + Preço Teto/abaixo-do-teto (Bazin).
- [x] Frontend `Valuation`: tabela de ranking + calculadoras Graham e Bazin.

## Fase 4 — Gerenciador de carteira & rentabilidade (CONCLUÍDA)
**Objetivo:** o "coração" do cockpit.
- [x] Preço médio ponderado por transação de COMPRA (trata VENDA).
- [x] Consolidação por classe de ativo e setor.
- [x] Evolução patrimonial (série temporal patrimônio vs investido).
- [x] Benchmark **CDI** sobreposto na curva (aportes corrigidos pelo CDI/BCB).
- [x] Frontend `Dashboard`/`Carteira`: cards, área de evolução e pizzas (Recharts).
- [ ] TWR (Time-Weighted Return) formal vs Ibovespa (refinamento futuro).

## Fase 5 — Importação de extratos B3/corretora (CONCLUÍDA)
**Objetivo:** acabar com a digitação manual.
- [x] `integrations/importador_b3.py`: parser XLSX (pandas/openpyxl) tolerante a layout.
- [x] Rota `/transacoes/importar`: cria ativos ausentes e deduplica transações.
- [x] Frontend `Carteira`: upload de extrato com feedback (inseridas/duplicadas).
- [ ] Parser PDF (extrato de movimentação) — futuro.

## Fase 6 — Dividendos Inteligentes (previsão) (CONCLUÍDA)
**Objetivo:** agenda preditiva.
- [x] `services/dividendos_ia.py`: distribuição probabilística por mês (sazonalidade).
- [x] Rota `/proventos/agenda-preditiva` (carteira + por ativo).
- [x] Yield on Cost e evolução de proventos (`/proventos/resumo`).
- [x] Frontend `Dividendos`: gráfico de evolução + heatmap da agenda preditiva.

## Fase 7 — Módulo Fiscal (Isentômetro & IR) (CONCLUÍDA)
**Objetivo:** apoio às obrigações com o Fisco.
- [x] Isentômetro: VENDAS do mês vs teto (R$ 20.000) — status verde/amarelo/vermelho.
- [x] Lucro realizado + imposto estimado (15% swing trade) quando acima do teto.
- [x] Relatório IR: posição 31/12 (Bens e Direitos) com preço médio e discriminação.
- [x] Frontend `Fiscal`: barra de progresso + cards + tabela de Bens e Direitos.
- [ ] Emissão de DARF formal — futuro.

## Fase 8 — Agendamentos (cronjobs) (CONCLUÍDA)
**Objetivo:** automação em segundo plano.
- [x] `atualizar_cotacoes`: seg–sex 18h (APScheduler, fuso America/Sao_Paulo).
- [x] `atualizar_fundamentalista`: domingos 08h (recalcular fundamentos).
- [x] Liga/desliga via `ENABLE_SCHEDULER` no `.env` (off em dev com --reload).
- [x] Logs das execuções via logger do uvicorn.

## Fase 9 — Qualidade e produção
- [ ] Autenticação (uso pessoal — login simples / token).
- [ ] Testes ampliados + CI.
- [ ] TimescaleDB para séries de cotações (opcional).
- [ ] Build de produção do frontend + deploy.

---

## Convenções
- **Backend:** rotas em `app/api/routes`, regra de negócio em `app/services`,
  acesso externo em `app/integrations`, jobs em `app/tasks`.
- **Frontend:** páginas em `src/pages`, componentes reutilizáveis em
  `src/components`, chamadas HTTP centralizadas em `src/lib/api.ts`.
- **Fórmulas-chave:**
  - Graham: `preco_justo = sqrt(22.5 * LPA * VPA)` (apenas se LPA>0 e VPA>0).
  - Bazin: `preco_teto = dividendos_medios_5_anos / 0.06`.
  - Upside: `((preco_referencia / preco_atual) - 1) * 100`.

## Status atual
Fases 1–8 **concluídas**. Pendências opcionais (Fase 9 / refinamentos):
- Autenticação pessoal (login/token).
- TWR formal e benchmark Ibovespa.
- Parser de PDF e emissão de DARF.
- TimescaleDB para séries; CI; deploy de produção.
