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

## Fase 1 — Persistência e CRUD básico
**Objetivo:** banco vivo com dados manuais.
- [ ] Configurar **Alembic** (migrations) e gerar o schema inicial.
- [ ] Schemas Pydantic (entrada/saída) para `Ativo`, `Transacao`, `Provento`.
- [ ] Implementar CRUD real em `ativos`, `transacoes`, `proventos` (substituir stubs).
- [ ] Seed de dados de exemplo (alguns tickers + transações fictícias).
- [ ] Testes de API (pytest + httpx) para os CRUDs.

## Fase 2 — Ingestão de dados de mercado
**Objetivo:** preencher cotações e fundamentos automaticamente.
- [ ] `integrations/brapi.py`: cotações e dividendos da B3 (token via `.env`).
- [ ] `integrations/yahoo.py`: fundamentos (LPA, VPA) e ativos internacionais.
- [ ] `integrations/bcb.py`: séries CDI (12), IPCA (433), Selic (11).
- [ ] Persistir em `cotacoes_historicas` e `indicadores_fundamentalistas`.
- [ ] Tratamento de erros/timeout e cache para não estourar limites de API.

## Fase 3 — Valuation (Graham & Bazin)
**Objetivo:** rankings de margem de segurança.
- [ ] Ligar `services/valuation.py` aos dados de `indicadores_fundamentalistas`.
- [ ] Rota `/valuation/ranking`: Upside (Graham) e abaixo-do-teto (Bazin).
- [ ] Frontend `Valuation`: calculadoras + tabela de ranking ordenável.

## Fase 4 — Gerenciador de carteira & rentabilidade
**Objetivo:** o "coração" do cockpit.
- [ ] Preço médio ponderado por transação de COMPRA.
- [ ] TWR (Time-Weighted Return) com pandas; comparação vs Ibovespa e CDI.
- [ ] Consolidação por classe de ativo, setor e moeda (agregações SQL).
- [ ] Frontend `Dashboard`/`Carteira`: cards, gráfico de linha e pizza (Recharts).

## Fase 5 — Importação de extratos B3/corretora
**Objetivo:** acabar com a digitação manual.
- [ ] `integrations/importador_b3.py`: parser XLSX (pandas/openpyxl).
- [ ] Parser PDF (extrato de movimentação).
- [ ] Rota `/transacoes/importar` com validação e deduplicação.
- [ ] Frontend: upload com preview antes de gravar.

## Fase 6 — Dividendos Inteligentes (previsão)
**Objetivo:** agenda preditiva.
- [ ] `services/dividendos_ia.py`: análise de `data_com` (5–7 anos) com scikit-learn.
- [ ] Distribuição probabilística por mês; rota `/proventos/agenda-preditiva`.
- [ ] Yield on Cost e evolução de proventos (mês a mês / ano a ano).
- [ ] Frontend `Dividendos`: gráfico de evolução + agenda preditiva.

## Fase 7 — Módulo Fiscal (Isentômetro & IR)
**Objetivo:** apoio às obrigações com o Fisco.
- [ ] Isentômetro: soma de VENDAS do mês vs teto (R$ 20.000 ações) — verde/amarelo/vermelho.
- [ ] Gerador de relatório IR: posição 31/12 (Bens e Direitos) com CNPJ e preço médio.
- [ ] Cálculo/emissão de DARF (ganho de capital acima da isenção).
- [ ] Frontend `Fiscal`: barra de progresso + exportação do relatório.

## Fase 8 — Agendamentos (cronjobs)
**Objetivo:** automação em segundo plano.
- [ ] `Task_Atualizar_Cotacoes`: seg–sex 18h (APScheduler ou Celery beat + Redis).
- [ ] `Task_Atualizar_Fundamentalista`: domingos (recalcular rankings).
- [ ] Logs e monitoramento das execuções.

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

## Próximo passo sugerido
Iniciar a **Fase 1** (Alembic + CRUD real + seed), pois destrava todas as
demais fases. Posso assumir essa fase quando você quiser.
