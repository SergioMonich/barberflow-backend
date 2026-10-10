from fastapi.testclient import TestClient
from tests.conftest import registrar_e_logar


def criar_servico(client: TestClient, headers: dict, nome: str = "Corte") -> dict:

    resposta = client.post(

        "/servicos",
        json={"nome": nome, "preco": 35.0, "duracao_minutos": 40},
        headers=headers,

    )

    assert resposta.status_code == 201
    return resposta.json()


def test_rotas_de_servicos_exigem_login(client: TestClient):

    assert client.get("/servicos").status_code == 401
    assert client.post("/servicos", json={"nome": "X", "preco": 1}).status_code == 401


def test_criar_servico(client: TestClient, auth_headers: dict):

    servico = criar_servico(client, auth_headers)

    assert servico["nome"] == "Corte"
    assert servico["preco"] == 35.0
    assert servico["ativo"] is True


def test_preco_zero_ou_negativo_retorna_422(client: TestClient, auth_headers: dict):

    for preco in (0, -10):

        resposta = client.post(

            "/servicos", json={"nome": "X", "preco": preco}, headers=auth_headers

        )

        assert resposta.status_code == 422


def test_atualizar_so_o_preco_preserva_o_resto(client: TestClient, auth_headers: dict):

    criado = criar_servico(client, auth_headers)

    resposta = client.put(

        f"/servicos/{criado['id']}", json={"preco": 45.0}, headers=auth_headers

    )

    assert resposta.status_code == 200
    assert resposta.json()["preco"] == 45.0
    assert resposta.json()["nome"] == "Corte"
    assert resposta.json()["duracao_minutos"] == 40


def test_delete_desativa_e_some_da_lista(client: TestClient, auth_headers: dict):

    criado = criar_servico(client, auth_headers)

    assert client.delete(f"/servicos/{criado['id']}", headers=auth_headers).status_code == 204
    assert client.get("/servicos", headers=auth_headers).json() == []
    assert client.get(f"/servicos/{criado['id']}", headers=auth_headers).status_code == 404


def test_isolamento_entre_barbearias(client: TestClient):
    
    headers_a = registrar_e_logar(client, "a@email.com", "Barbearia A")
    headers_b = registrar_e_logar(client, "b@email.com", "Barbearia B")
    servico_da_a = criar_servico(client, headers_a, "Corte da A")
    url = f"/servicos/{servico_da_a['id']}"

    assert client.get("/servicos", headers=headers_b).json() == []
    assert client.get(url, headers=headers_b).status_code == 404
    assert client.put(url, json={"nome": "Hack"}, headers=headers_b).status_code == 404
    assert client.delete(url, headers=headers_b).status_code == 404
    assert client.get(url, headers=headers_a).status_code == 200