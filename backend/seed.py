"""Popula o banco com dados de exemplo para desenvolvimento.

Uso: python seed.py
"""

from datetime import date

from app.core.database import Base, SessionLocal, engine
from app.models import (
    Ativo,
    CotacaoHistorica,
    IndicadorFundamentalista,
    ProventoRecebido,
    Transacao,
)

ATIVOS = [
    {"ticker": "PETR4", "nome": "Petrobras PN", "tipo": "Acao", "setor": "Petróleo e Gás"},
    {"ticker": "ITUB4", "nome": "Itaú Unibanco PN", "tipo": "Acao", "setor": "Bancos"},
    {"ticker": "TAEE11", "nome": "Taesa Unit", "tipo": "Acao", "setor": "Energia Elétrica"},
    {"ticker": "HGLG11", "nome": "CSHG Logística FII", "tipo": "FII", "setor": "Logística"},
]

INDICADORES = {
    "PETR4": {"lpa": 7.5, "vpa": 30.0, "p_l": 4.5, "roe": 0.30, "dividend_yield": 0.14},
    "ITUB4": {"lpa": 3.2, "vpa": 14.0, "p_l": 9.0, "roe": 0.20, "dividend_yield": 0.06},
    "TAEE11": {"lpa": 3.0, "vpa": 16.0, "p_l": 11.0, "roe": 0.18, "dividend_yield": 0.09},
}


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Limpa dados anteriores para que o seed seja re-executável.
        for model in (ProventoRecebido, Transacao, CotacaoHistorica, IndicadorFundamentalista, Ativo):
            db.query(model).delete()
        db.commit()

        ativos: dict[str, Ativo] = {}
        for data in ATIVOS:
            ativo = Ativo(**data)
            db.add(ativo)
            ativos[data["ticker"]] = ativo
        db.flush()

        for ticker, ind in INDICADORES.items():
            db.add(IndicadorFundamentalista(ativo_id=ativos[ticker].id, **ind))

        db.add_all([
            Transacao(ativo_id=ativos["PETR4"].id, tipo_operacao="COMPRA",
                      data_operacao=date(2024, 1, 10), quantidade=100, preco_unitario=36.50, taxas_corretagem=0),
            Transacao(ativo_id=ativos["ITUB4"].id, tipo_operacao="COMPRA",
                      data_operacao=date(2024, 2, 5), quantidade=200, preco_unitario=28.00, taxas_corretagem=0),
            Transacao(ativo_id=ativos["HGLG11"].id, tipo_operacao="COMPRA",
                      data_operacao=date(2024, 3, 1), quantidade=50, preco_unitario=160.00, taxas_corretagem=0),
        ])

        db.add_all([
            ProventoRecebido(ativo_id=ativos["PETR4"].id, data_pagamento=date(2024, 5, 20),
                             data_com=date(2024, 5, 2), tipo_provento="Dividendo", valor_liquido=250.00),
            ProventoRecebido(ativo_id=ativos["HGLG11"].id, data_pagamento=date(2024, 4, 15),
                             data_com=date(2024, 3, 28), tipo_provento="Dividendo", valor_liquido=55.00),
        ])

        # Cotações mensais (jan→jun/2024) para alimentar o gráfico de evolução.
        historico = {
            "PETR4": [36.50, 37.10, 35.80, 39.20, 37.90, 38.20],
            "ITUB4": [27.90, 28.40, 29.10, 30.50, 32.00, 33.10],
            "TAEE11": [35.00, 35.40, 36.10, 35.90, 36.20, 36.40],
            "HGLG11": [158.00, 159.50, 161.00, 162.50, 163.80, 165.00],
        }
        for ticker, precos in historico.items():
            for mes, preco in enumerate(precos, start=1):
                db.add(CotacaoHistorica(
                    ativo_id=ativos[ticker].id,
                    data=date(2024, mes, 3),
                    preco_fechamento=preco,
                ))

        db.commit()
        print(f"Seed concluído: {len(ATIVOS)} ativos inseridos.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
