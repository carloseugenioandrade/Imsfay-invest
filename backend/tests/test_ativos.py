def test_criar_e_listar_ativo(client):
    resp = client.post("/api/ativos", json={
        "ticker": "PETR4",
        "nome": "Petrobras PN",
        "tipo": "Acao",
        "setor": "Petróleo",
    })
    assert resp.status_code in (200, 201), resp.text
    criado = resp.json()
    assert criado["ticker"] == "PETR4"
    assert criado["id"] > 0

    lista = client.get("/api/ativos").json()
    assert any(a["ticker"] == "PETR4" for a in lista)


def test_ticker_duplicado_rejeitado(client):
    payload = {"ticker": "ITUB4", "nome": "Itaú", "tipo": "Acao"}
    assert client.post("/api/ativos", json=payload).status_code in (200, 201)
    segundo = client.post("/api/ativos", json=payload)
    assert segundo.status_code == 409
