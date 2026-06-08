"""Testes do parser de extrato XLSX da B3."""

from io import BytesIO

import pandas as pd

from app.integrations.importador_b3 import _parse_pdf_texto, parse_extrato_xlsx
from app.services.dividendos_ia import prever_meses_provento
from datetime import date


def _xlsx(rows: list[dict]) -> bytes:
    buf = BytesIO()
    pd.DataFrame(rows).to_excel(buf, index=False)
    return buf.getvalue()


def test_parse_extrato_negociacao():
    conteudo = _xlsx([
        {"Data do Negócio": "10/01/2024", "Tipo de Movimentação": "Compra",
         "Código de Negociação": "PETR4", "Quantidade": 100, "Preço": "30,50"},
        {"Data do Negócio": "11/01/2024", "Tipo de Movimentação": "Venda",
         "Código de Negociação": "ITUB4 - ITAU PN", "Quantidade": 50, "Preço": "28,00"},
    ])
    linhas = parse_extrato_xlsx(conteudo)
    assert len(linhas) == 2
    assert linhas[0]["ticker"] == "PETR4"
    assert linhas[0]["tipo_operacao"] == "COMPRA"
    assert linhas[0]["preco_unitario"] == 30.5
    assert linhas[1]["ticker"] == "ITUB4"
    assert linhas[1]["tipo_operacao"] == "VENDA"


def test_parse_pdf_texto():
    texto = (
        "Negociação de Ativos\n"
        "10/01/2024 C PETR4 100 30,50\n"
        "11/01/2024 Venda ITUB4 50 R$ 28,00\n"
        "linha sem transacao\n"
    )
    linhas = _parse_pdf_texto(texto)
    assert len(linhas) == 2
    assert linhas[0]["ticker"] == "PETR4"
    assert linhas[0]["tipo_operacao"] == "COMPRA"
    assert linhas[0]["quantidade"] == 100
    assert linhas[0]["preco_unitario"] == 30.5
    assert linhas[1]["ticker"] == "ITUB4"
    assert linhas[1]["tipo_operacao"] == "VENDA"
    assert linhas[1]["preco_unitario"] == 28.0


def test_importar_endpoint(client):
    conteudo = _xlsx([
        {"Data do Negócio": "10/01/2024", "Tipo de Movimentação": "Compra",
         "Código de Negociação": "WEGE3", "Quantidade": 10, "Preço": "40,00"},
    ])
    resp = client.post(
        "/api/transacoes/importar",
        files={"file": ("negociacao.xlsx", conteudo,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["inseridas"] == 1
    assert data["ativos_criados"] == 1
    # Reimportar deve deduplicar.
    resp2 = client.post(
        "/api/transacoes/importar",
        files={"file": ("negociacao.xlsx", conteudo,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert resp2.json()["duplicadas"] == 1


def test_previsao_dividendos_sazonalidade():
    datas = [date(2022, 5, 10), date(2023, 5, 12), date(2022, 11, 1)]
    prob = prever_meses_provento(datas)
    # Maio aparece em 2 anos de 2 observados -> 1.0; Nov em 1 de 2 -> 0.5.
    assert prob[5] == 1.0
    assert prob[11] == 0.5
    assert prob[1] == 0.0
