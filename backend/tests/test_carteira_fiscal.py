"""Testes de ponta a ponta para carteira, fiscal e valuation."""


def _criar_ativo(client, ticker="PETR4"):
    r = client.post("/api/ativos", json={"ticker": ticker, "nome": ticker, "tipo": "Acao", "setor": "Energia"})
    return r.json()["id"]


def _compra(client, ativo_id, data, qtd, preco):
    return client.post("/api/transacoes", json={
        "ativo_id": ativo_id,
        "tipo_operacao": "COMPRA",
        "data_operacao": data,
        "quantidade": qtd,
        "preco_unitario": preco,
        "taxas_corretagem": 0,
    })


def test_resumo_carteira_preco_medio(client):
    aid = _criar_ativo(client)
    assert _compra(client, aid, "2024-01-10", 100, 30.0).status_code in (200, 201)
    assert _compra(client, aid, "2024-02-10", 100, 40.0).status_code in (200, 201)

    resumo = client.get("/api/carteira/resumo").json()
    # Investido = 100*30 + 100*40 = 7000; preço médio = 35.
    assert resumo["valor_investido"] == 7000.0
    assert resumo["quantidade_ativos"] == 1


def test_isentometro_abaixo_do_teto(client):
    aid = _criar_ativo(client)
    _compra(client, aid, "2024-01-10", 100, 30.0)
    # Venda de R$ 5.000 < teto de 20k -> isento.
    client.post("/api/transacoes", json={
        "ativo_id": aid, "tipo_operacao": "VENDA", "data_operacao": "2024-03-10",
        "quantidade": 100, "preco_unitario": 50.0, "taxas_corretagem": 0,
    })
    iso = client.get("/api/fiscal/isentometro?ano=2024&mes=3").json()
    assert iso["total_vendas"] == 5000.0
    assert iso["isento"] is True
    assert iso["status"] == "verde"
    # Lucro = (50-30)*100 = 2000.
    assert iso["lucro_realizado"] == 2000.0
    assert iso["imposto_estimado"] == 0.0


def test_relatorio_ir_posicao(client):
    aid = _criar_ativo(client)
    _compra(client, aid, "2024-01-10", 100, 30.0)
    ir = client.get("/api/fiscal/relatorio-ir?ano=2024").json()
    assert ir["total"] == 3000.0
    assert ir["itens"][0]["ticker"] == "PETR4"
    assert ir["itens"][0]["preco_medio"] == 30.0


def test_valuation_graham(client):
    r = client.get("/api/valuation/graham?lpa=4&vpa=10&preco_atual=20").json()
    # √(22,5*4*10) = √900 = 30.
    assert round(r["preco_justo"], 2) == 30.0
    assert round(r["upside_pct"], 2) == 50.0
