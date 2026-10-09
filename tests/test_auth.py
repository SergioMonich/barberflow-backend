from fastapi.testclient import TestClient

DADOS_REGISTRO = {
    "nome": "Sergio",
    "email": "sergio@email.com",
    "senha": "senha123",
    "nome_barbearia": "Barbearia do Sergio",
}


def test_registro_cria_usuario_sem_expor_senha(client: TestClient):
    resposta = client.post("/auth/registro", json=DADOS_REGISTRO)

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["email"] == "sergio@email.com"
    assert "senha" not in corpo
    assert "senha_hash" not in corpo


def test_registro_com_email_repetido_retorna_400(client: TestClient):
    client.post("/auth/registro", json=DADOS_REGISTRO)

    resposta = client.post("/auth/registro", json=DADOS_REGISTRO)

    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Email ja cadastrado"


def test_registro_com_email_invalido_retorna_422(client: TestClient):
    dados = {**DADOS_REGISTRO, "email": "isto-nao-e-um-email"}

    resposta = client.post("/auth/registro", json=dados)

    assert resposta.status_code == 422


def test_login_com_credenciais_corretas_retorna_token(client: TestClient):
    client.post("/auth/registro", json=DADOS_REGISTRO)

    resposta = client.post(
        "/auth/login",
        data={"username": "sergio@email.com", "password": "senha123"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["token_type"] == "bearer"
    assert resposta.json()["access_token"]


def test_login_com_senha_errada_retorna_401(client: TestClient):
    client.post("/auth/registro", json=DADOS_REGISTRO)

    resposta = client.post(
        "/auth/login",
        data={"username": "sergio@email.com", "password": "senha-errada"},
    )

    assert resposta.status_code == 401


def test_login_com_email_inexistente_retorna_a_mesma_mensagem(client: TestClient):
    resposta = client.post(
        "/auth/login",
        data={"username": "ninguem@email.com", "password": "qualquer"},
    )

    assert resposta.status_code == 401
    assert resposta.json()["detail"] == "Email ou senha incorretos"


def test_me_sem_token_retorna_401(client: TestClient):
    resposta = client.get("/auth/me")

    assert resposta.status_code == 401


def test_me_com_token_invalido_retorna_401(client: TestClient):
    resposta = client.get("/auth/me", headers={"Authorization": "Bearer token-falso"})

    assert resposta.status_code == 401


def test_me_com_token_valido_retorna_o_usuario(client: TestClient, auth_headers: dict):
    resposta = client.get("/auth/me", headers=auth_headers)

    assert resposta.status_code == 200
    assert resposta.json()["email"] == "dono@email.com"