# Imsfay Invest

Plataforma pessoal de análise e gestão de investimentos — o "Cockpit do Investidor de Longo Prazo".

Replica de forma privada e automatizada: gestão de carteira, automação de cotações, valuation clássico (Graham e Bazin), previsão preditiva de dividendos e controle fiscal (Isentômetro / auxílio IR) para ativos nacionais e internacionais.

> **Status:** esqueleto do projeto (estrutura + plano). A lógica de negócio ainda será implementada por etapas — veja [`docs/PLANO.md`](docs/PLANO.md).

---

## Stack

| Camada | Tecnologia |
| --- | --- |
| Backend | Python 3.11+, FastAPI, SQLAlchemy, Pydantic |
| Cálculo | pandas, numpy, scikit-learn |
| Frontend | React + Vite + TypeScript, Tailwind CSS, Recharts |
| Banco | PostgreSQL (+ TimescaleDB opcional) |
| Filas/Agendamento | Celery + Redis (ou APScheduler) |
| Integrações | Brapi, Yahoo Finance (`yfinance`), Banco Central (SGS) |

---

## Estrutura do repositório

```
Imsfay/
├── backend/            # API FastAPI + serviços + integrações + tarefas
├── frontend/           # Dashboard React/Vite/TS + Tailwind
├── docs/               # Documentação e plano de execução
├── docker-compose.yml  # Postgres + Redis + backend + frontend
├── .env.example        # Variáveis de ambiente (modelo)
└── README.md
```

---

## Como rodar (desenvolvimento)

### Pré-requisitos
- Docker + Docker Compose **ou** Python 3.11+ e Node 18+ instalados localmente.

### Opção A — Docker (recomendado)
```bash
cp .env.example .env
docker compose up --build
```
- API: http://localhost:8000 (docs em `/docs`)
- Frontend: http://localhost:5173

### Opção B — Local

Backend:
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## Variáveis de ambiente

Veja [`.env.example`](.env.example). As principais:

| Variável | Descrição |
| --- | --- |
| `DATABASE_URL` | String de conexão PostgreSQL |
| `REDIS_URL` | Conexão Redis (filas/cache) |
| `BRAPI_TOKEN` | Token da API Brapi (cotações B3) |
| `VITE_API_URL` | URL base da API para o frontend |

---

## Roadmap

Consulte [`docs/PLANO.md`](docs/PLANO.md) para o plano detalhado por fases.
