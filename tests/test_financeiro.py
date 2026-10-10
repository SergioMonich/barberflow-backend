from fastapi.testclient import TestClient
from tests.conftest import registrar_e_logar
from tests.test_agendamentos import (

    DIA_20_MANHA,
    criar_agendamento,
    criar_cliente,
    criar_servico,
    mudar_status,

)


def criar_categoria(
        
    client: TestClient, headers: dict, nome: str = "Aluguel", tipo: str = "despesa"

) -> dict:
    
    resposta = client.post(

        "/financeiro/categorias", json={"nome": nome, "tipo": tipo}, headers=headers

    )

    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def lancar(
        
    client: TestClient,
    headers: dict,
    categoria: dict,
    valor: float,
    data: str = "2026-10-05",
    descricao: str | None = None,

):
    
    return client.post(

        "/financeiro/movimentacoes",
        json={

            "tipo": categoria["tipo"],
            "categoria_id": categoria["id"],
            "valor": valor,
            "data": data,
            "descricao": descricao,

        },

        headers=headers,

    )


def concluir_atendimento(
        
    client: TestClient, headers: dict, data_hora: str = DIA_20_MANHA, preco: float = 35.0

) -> dict:
    
    cliente = criar_cliente(client, headers)
    servico = criar_servico(client, headers, preco=preco)
    ag = criar_agendamento(client, headers, cliente["id"], servico["id"], data_hora)
    resposta = mudar_status(client, headers, ag["id"], "concluido")
    assert resposta.status_code == 200
    return ag


def test_rotas_financeiras_exigem_login(client: TestClient):

    assert client.get("/financeiro/categorias").status_code == 401
    assert client.post("/financeiro/categorias", json={}).status_code == 401
    assert client.get("/financeiro/movimentacoes").status_code == 401
    assert client.post("/financeiro/movimentacoes", json={}).status_code == 401
    assert client.delete("/financeiro/movimentacoes/1").status_code == 401
    assert client.get("/financeiro/resumo").status_code == 401


def test_criar_e_listar_categorias(client: TestClient, auth_headers: dict):

    criar_categoria(client, auth_headers, "Aluguel", "despesa")
    criar_categoria(client, auth_headers, "Gorjeta", "receita")

    todas = client.get("/financeiro/categorias", headers=auth_headers).json()
    despesas = client.get(

        "/financeiro/categorias", params={"tipo": "despesa"}, headers=auth_headers

    ).json()

    assert [c["nome"] for c in todas] == ["Aluguel", "Gorjeta"]
    assert [c["nome"] for c in despesas] == ["Aluguel"]


def test_categoria_duplicada_retorna_409(client: TestClient, auth_headers: dict):

    criar_categoria(client, auth_headers, "Aluguel", "despesa")

    resposta = client.post(

        "/financeiro/categorias",
        json={"nome": "Aluguel", "tipo": "despesa"},
        headers=auth_headers,

    )

    assert resposta.status_code == 409


def test_categoria_com_tipo_ou_nome_invalido_retorna_422(
        
    client: TestClient, auth_headers: dict

):
    
    tipo_ruim = client.post(

        "/financeiro/categorias",
        json={"nome": "X", "tipo": "doacao"},
        headers=auth_headers,
        
    )

    nome_vazio = client.post(

        "/financeiro/categorias",
        json={"nome": "", "tipo": "despesa"},
        headers=auth_headers,

    )

    assert tipo_ruim.status_code == 422
    assert nome_vazio.status_code == 422


def test_lancar_despesa_manual(client: TestClient, auth_headers: dict):

    aluguel = criar_categoria(client, auth_headers)

    resposta = lancar(client, auth_headers, aluguel, 800.0, descricao="Outubro")

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["tipo"] == "despesa"
    assert corpo["valor"] == 800.0
    assert corpo["data"] == "2026-10-05"
    assert corpo["agendamento_id"] is None


def test_valor_zero_ou_negativo_retorna_422(client: TestClient, auth_headers: dict):

    aluguel = criar_categoria(client, auth_headers)

    assert lancar(client, auth_headers, aluguel, 0).status_code == 422
    assert lancar(client, auth_headers, aluguel, -10).status_code == 422


def test_categoria_inexistente_ou_de_outra_barbearia_retorna_404(client: TestClient):

    headers_a = registrar_e_logar(client, "a@email.com", "Barbearia A")
    headers_b = registrar_e_logar(client, "b@email.com", "Barbearia B")
    categoria_a = criar_categoria(client, headers_a)

    inexistente = client.post(

        "/financeiro/movimentacoes",
        json={"tipo": "despesa", "categoria_id": 999, "valor": 10, "data": "2026-10-05"},
        headers=headers_b,

    )

    alheia = lancar(client, headers_b, categoria_a, 10)

    assert inexistente.status_code == 404
    assert alheia.status_code == 404


def test_tipo_da_movimentacao_deve_bater_com_o_da_categoria(
        
    client: TestClient, auth_headers: dict

):
    
    aluguel = criar_categoria(client, auth_headers, "Aluguel", "despesa")

    resposta = client.post(

        "/financeiro/movimentacoes",
        json={

            "tipo": "receita",
            "categoria_id": aluguel["id"],
            "valor": 10,
            "data": "2026-10-05",

        },

        headers=auth_headers,

    )

    assert resposta.status_code == 400


def test_concluir_atendimento_gera_receita_automatica(
        
    client: TestClient, auth_headers: dict

):
    
    ag = concluir_atendimento(client, auth_headers)

    movs = client.get("/financeiro/movimentacoes", headers=auth_headers).json()

    assert len(movs) == 1
    assert movs[0]["tipo"] == "receita"
    assert movs[0]["valor"] == 35.0
    assert movs[0]["agendamento_id"] == ag["id"]
    categorias = client.get("/financeiro/categorias", headers=auth_headers).json()
    assert [(c["nome"], c["tipo"]) for c in categorias] == [("Servicos", "receita")]


def test_receita_automatica_usa_o_valor_congelado(
        
    client: TestClient, auth_headers: dict

):
    
    cliente = criar_cliente(client, auth_headers)
    servico = criar_servico(client, auth_headers, preco=35.0)
    ag = criar_agendamento(client, auth_headers, cliente["id"], servico["id"])
    client.put(

        f"/servicos/{servico['id']}", json={"preco": 90.0}, headers=auth_headers

    )

    mudar_status(client, auth_headers, ag["id"], "concluido")

    movs = client.get("/financeiro/movimentacoes", headers=auth_headers).json()
    assert movs[0]["valor"] == 35.0


def test_receita_cai_no_dia_local_e_nao_no_dia_utc(
        
    client: TestClient, auth_headers: dict

):
    
    # 01:00 UTC do dia 21 = 22:00 do dia 20 em Brasilia
    concluir_atendimento(client, auth_headers, "2026-10-21T01:00:00Z")

    movs = client.get("/financeiro/movimentacoes", headers=auth_headers).json()

    assert movs[0]["data"] == "2026-10-20"


def test_cancelar_ou_faltar_nao_gera_receita(client: TestClient, auth_headers: dict):

    cliente = criar_cliente(client, auth_headers)
    servico = criar_servico(client, auth_headers)
    a = criar_agendamento(client, auth_headers, cliente["id"], servico["id"])
    b = criar_agendamento(

        client, auth_headers, cliente["id"], servico["id"], "2026-10-22T13:00:00Z"

    )

    mudar_status(client, auth_headers, a["id"], "cancelado")
    mudar_status(client, auth_headers, b["id"], "nao_compareceu")

    assert client.get("/financeiro/movimentacoes", headers=auth_headers).json() == []


def test_transicao_invalida_nao_gera_receita_duplicada(
        
    client: TestClient, auth_headers: dict

):
    
    ag = concluir_atendimento(client, auth_headers)

    repetido = mudar_status(client, auth_headers, ag["id"], "concluido")

    assert repetido.status_code == 409
    movs = client.get("/financeiro/movimentacoes", headers=auth_headers).json()
    assert len(movs) == 1


def test_listar_por_periodo_inclusivo_e_por_tipo(
        
    client: TestClient, auth_headers: dict

):
    
    aluguel = criar_categoria(client, auth_headers, "Aluguel", "despesa")
    gorjeta = criar_categoria(client, auth_headers, "Gorjeta", "receita")
    lancar(client, auth_headers, aluguel, 100, "2026-10-01")
    lancar(client, auth_headers, gorjeta, 20, "2026-10-10")
    lancar(client, auth_headers, aluguel, 50, "2026-10-31")

    periodo = client.get(

        "/financeiro/movimentacoes",
        params={"inicio": "2026-10-10", "fim": "2026-10-31"},
        headers=auth_headers,

    ).json()

    so_receitas = client.get(

        "/financeiro/movimentacoes", params={"tipo": "receita"}, headers=auth_headers

    ).json()

    assert [m["valor"] for m in periodo] == [20, 50]
    assert [m["valor"] for m in so_receitas] == [20]


def test_periodo_invertido_retorna_400(client: TestClient, auth_headers: dict):

    params = {"inicio": "2026-10-31", "fim": "2026-10-01"}

    assert (

        client.get(

            "/financeiro/movimentacoes", params=params, headers=auth_headers

        ).status_code == 400

    )

    assert (

        client.get("/financeiro/resumo", params=params, headers=auth_headers).status_code == 400

    )


def test_resumo_soma_receitas_despesas_e_saldo(client: TestClient, auth_headers: dict):

    aluguel = criar_categoria(client, auth_headers, "Aluguel", "despesa")
    lancar(client, auth_headers, aluguel, 800.0, "2026-10-05")
    concluir_atendimento(client, auth_headers, "2026-10-20T13:00:00Z", preco=35.0)
    concluir_atendimento(client, auth_headers, "2026-10-21T13:00:00Z", preco=50.5)

    resposta = client.get("/financeiro/resumo", headers=auth_headers)

    assert resposta.status_code == 200
    assert resposta.json() == {

        "inicio": None,
        "fim": None,
        "receitas": 85.5,
        "despesas": 800.0,
        "saldo": -714.5,
        "quantidade": 3,

    }


def test_resumo_respeita_o_periodo(client: TestClient, auth_headers: dict):

    aluguel = criar_categoria(client, auth_headers, "Aluguel", "despesa")
    lancar(client, auth_headers, aluguel, 800.0, "2026-10-05")
    concluir_atendimento(client, auth_headers, "2026-10-20T13:00:00Z", preco=35.0)

    resposta = client.get(

        "/financeiro/resumo",
        params={"inicio": "2026-10-20", "fim": "2026-10-20"},
        headers=auth_headers,

    ).json()

    assert resposta["receitas"] == 35.0
    assert resposta["despesas"] == 0
    assert resposta["saldo"] == 35.0
    assert resposta["quantidade"] == 1


def test_resumo_vazio_retorna_zeros(client: TestClient, auth_headers: dict):

    resposta = client.get("/financeiro/resumo", headers=auth_headers).json()

    assert resposta["receitas"] == 0
    assert resposta["despesas"] == 0
    assert resposta["saldo"] == 0
    assert resposta["quantidade"] == 0


def test_excluir_despesa_manual(client: TestClient, auth_headers: dict):

    aluguel = criar_categoria(client, auth_headers)
    mov = lancar(client, auth_headers, aluguel, 800.0).json()

    apagar = client.delete(

        f"/financeiro/movimentacoes/{mov['id']}", headers=auth_headers

    )

    assert apagar.status_code == 204
    assert client.get("/financeiro/movimentacoes", headers=auth_headers).json() == []


def test_receita_de_atendimento_nao_pode_ser_excluida(
        
    client: TestClient, auth_headers: dict

):
    
    concluir_atendimento(client, auth_headers)
    mov = client.get("/financeiro/movimentacoes", headers=auth_headers).json()[0]

    apagar = client.delete(

        f"/financeiro/movimentacoes/{mov['id']}", headers=auth_headers

    )

    assert apagar.status_code == 409


def test_excluir_movimentacao_inexistente_retorna_404(
        
    client: TestClient, auth_headers: dict

):
    resposta = client.delete("/financeiro/movimentacoes/999", headers=auth_headers)

    assert resposta.status_code == 404


def test_isolamento_financeiro_entre_barbearias(client: TestClient):

    headers_a = registrar_e_logar(client, "a@email.com", "Barbearia A")
    headers_b = registrar_e_logar(client, "b@email.com", "Barbearia B")
    aluguel = criar_categoria(client, headers_a)
    mov = lancar(client, headers_a, aluguel, 800.0).json()
    concluir_atendimento(client, headers_a)

    assert client.get("/financeiro/categorias", headers=headers_b).json() == []
    assert client.get("/financeiro/movimentacoes", headers=headers_b).json() == []
    assert client.get("/financeiro/resumo", headers=headers_b).json()["quantidade"] == 0
    assert (

        client.delete(

            f"/financeiro/movimentacoes/{mov['id']}", headers=headers_b

        ).status_code == 404

    )
    
    assert len(client.get("/financeiro/movimentacoes", headers=headers_a).json()) == 2