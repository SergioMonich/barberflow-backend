from fastapi.testclient import TestClient

from tests.conftest import registrar_e_logar


def criar_cliente(client: TestClient, headers: dict, nome: str = "Joao") -> dict:
    resposta = client.post(
        "/clientes",
        json={"nome": nome, "telefone": "44911112222", "email": "joao@email.com"},
        headers=headers,
    )
    assert resposta.status_code == 201
    return resposta.json()


def test_rotas_de_clientes_exigem_login(client: TestClient):
    assert client.get("/clientes").status_code == 401
    assert client.post("/clientes", json={"nome": "X"}).status_code == 401
    assert client.get("/clientes/1").status_code == 401
    assert client.put("/clientes/1", json={"nome": "X"}).status_code == 401
    assert client.delete("/clientes/1").status_code == 401


def test_criar_cliente_associa_a_barbearia_do_usuario(
    client: TestClient, auth_headers: dict
):
    cliente = criar_cliente(client, auth_headers)

    assert cliente["id"]
    assert cliente["nome"] == "Joao"
    assert cliente["barbearia_id"]


def test_criar_cliente_sem_nome_retorna_422(client: TestClient, auth_headers: dict):
    resposta = client.post("/clientes", json={"telefone": "1"}, headers=auth_headers)

    assert resposta.status_code == 422


def test_listar_clientes(client: TestClient, auth_headers: dict):
    criar_cliente(client, auth_headers, "Ana")
    criar_cliente(client, auth_headers, "Bruno")

    resposta = client.get("/clientes", headers=auth_headers)

    assert resposta.status_code == 200
    nomes = [c["nome"] for c in resposta.json()]
    assert nomes == ["Ana", "Bruno"]


def test_buscar_cliente_por_id(client: TestClient, auth_headers: dict):
    criado = criar_cliente(client, auth_headers)

    resposta = client.get(f"/clientes/{criado['id']}", headers=auth_headers)

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Joao"


def test_buscar_cliente_inexistente_retorna_404(
    client: TestClient, auth_headers: dict
):
    resposta = client.get("/clientes/9999", headers=auth_headers)

    assert resposta.status_code == 404


def test_atualizar_so_o_telefone_preserva_os_outros_campos(
    client: TestClient, auth_headers: dict
):
    criado = criar_cliente(client, auth_headers)

    resposta = client.put(
        f"/clientes/{criado['id']}",
        json={"telefone": "44999999999"},
        headers=auth_headers,
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["telefone"] == "44999999999"
    assert corpo["nome"] == "Joao"
    assert corpo["email"] == "joao@email.com"


def test_deletar_cliente(client: TestClient, auth_headers: dict):
    criado = criar_cliente(client, auth_headers)

    resposta = client.delete(f"/clientes/{criado['id']}", headers=auth_headers)

    assert resposta.status_code == 204
    depois = client.get(f"/clientes/{criado['id']}", headers=auth_headers)
    assert depois.status_code == 404


# --- Isolamento entre barbearias: a regra de seguranca mais importante ---


def test_usuario_nao_ve_clientes_de_outra_barbearia(client: TestClient):
    headers_a = registrar_e_logar(client, "a@email.com", "Barbearia A")
    headers_b = registrar_e_logar(client, "b@email.com", "Barbearia B")
    criar_cliente(client, headers_a, "Cliente da A")

    resposta = client.get("/clientes", headers=headers_b)

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_usuario_nao_acessa_cliente_de_outra_barbearia_por_id(client: TestClient):
    headers_a = registrar_e_logar(client, "a@email.com", "Barbearia A")
    headers_b = registrar_e_logar(client, "b@email.com", "Barbearia B")
    cliente_da_a = criar_cliente(client, headers_a, "Cliente da A")
    url = f"/clientes/{cliente_da_a['id']}"

    # 404 (e nao 403): nao revela que o cliente existe na conta de outra pessoa.
    assert client.get(url, headers=headers_b).status_code == 404
    assert client.put(url, json={"nome": "Hack"}, headers=headers_b).status_code == 404
    assert client.delete(url, headers=headers_b).status_code == 404

    # E o cliente da A continua intacto.
    intacto = client.get(url, headers=headers_a)
    assert intacto.status_code == 200
    assert intacto.json()["nome"] == "Cliente da A"