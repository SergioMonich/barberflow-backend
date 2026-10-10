from fastapi.testclient import TestClient
from tests.conftest import registrar_e_logar

DIA_20_MANHA = "2026-10-20T13:00:00Z"
DIA_20_TARDE = "2026-10-20T18:00:00Z"
DIA_21_MANHA = "2026-10-21T13:00:00Z"


def criar_cliente(client: TestClient, headers: dict, nome: str = "Joao") -> dict:

    resposta = client.post("/clientes", json={"nome": nome}, headers=headers)
    assert resposta.status_code == 201
    return resposta.json()


def criar_servico(
        
    client: TestClient, headers: dict, nome: str = "Corte", preco: float = 35.0

) -> dict:
    
    resposta = client.post(

        "/servicos", json={"nome": nome, "preco": preco}, headers=headers

    )

    assert resposta.status_code == 201
    return resposta.json()


def criar_agendamento(
        
    client: TestClient,
    headers: dict,
    cliente_id: int,
    servico_id: int,
    data_hora: str = DIA_20_MANHA,

) -> dict:
    
    resposta = client.post(

        "/agendamentos",
        json={

            "cliente_id": cliente_id,
            "servico_id": servico_id,
            "data_hora": data_hora,

        },

        headers=headers,

    )

    assert resposta.status_code == 201, resposta.text
    return resposta.json()


def mudar_status(client: TestClient, headers: dict, agendamento_id: int, novo: str):

    return client.patch(

        f"/agendamentos/{agendamento_id}/status",
        json={"status": novo},
        headers=headers,

    )


def preparar(client: TestClient, headers: dict) -> tuple[dict, dict]:

    return criar_cliente(client, headers), criar_servico(client, headers)


def test_rotas_de_agendamentos_exigem_login(client: TestClient):

    assert client.get("/agendamentos").status_code == 401
    assert client.post("/agendamentos", json={}).status_code == 401
    assert client.get("/agendamentos/1").status_code == 401
    assert client.put("/agendamentos/1", json={}).status_code == 401
    assert client.patch("/agendamentos/1/status", json={}).status_code == 401


def test_criar_agendamento_copia_o_preco_e_comeca_como_agendado(
        
    client: TestClient, auth_headers: dict

):
    
    cliente, servico = preparar(client, auth_headers)

    ag = criar_agendamento(client, auth_headers, cliente["id"], servico["id"])

    assert ag["status"] == "agendado"
    assert ag["valor"] == 35.0
    assert ag["cliente_id"] == cliente["id"]
    assert ag["servico_id"] == servico["id"]
    assert ag["barbeiro_id"]


def test_valor_fica_congelado_quando_o_preco_do_servico_muda(
        
    client: TestClient, auth_headers: dict

):
    
    cliente, servico = preparar(client, auth_headers)
    antigo = criar_agendamento(client, auth_headers, cliente["id"], servico["id"])

    client.put(

        f"/servicos/{servico['id']}", json={"preco": 50.0}, headers=auth_headers

    )

    novo = criar_agendamento(

        client, auth_headers, cliente["id"], servico["id"], DIA_21_MANHA

    )

    depois = client.get(f"/agendamentos/{antigo['id']}", headers=auth_headers).json()
    assert depois["valor"] == 35.0
    assert novo["valor"] == 50.0


def test_agendamentos_do_mesmo_dono_usam_o_mesmo_barbeiro(
        
    client: TestClient, auth_headers: dict

):
    
    cliente, servico = preparar(client, auth_headers)

    a = criar_agendamento(client, auth_headers, cliente["id"], servico["id"])
    b = criar_agendamento(
        client, auth_headers, cliente["id"], servico["id"], DIA_21_MANHA

    )

    assert a["barbeiro_id"] == b["barbeiro_id"]


def test_data_sem_fuso_e_aceita(client: TestClient, auth_headers: dict):

    cliente, servico = preparar(client, auth_headers)

    ag = criar_agendamento(

        client, auth_headers, cliente["id"], servico["id"], "2026-10-20T13:00:00"

    )

    assert ag["id"]


def test_cliente_ou_servico_inexistente_retorna_404(
        
    client: TestClient, auth_headers: dict

):
    
    cliente, servico = preparar(client, auth_headers)

    sem_cliente = client.post(

        "/agendamentos",
        json={"cliente_id": 999, "servico_id": servico["id"], "data_hora": DIA_20_MANHA},
        headers=auth_headers,

    )

    sem_servico = client.post(

        "/agendamentos",
        json={"cliente_id": cliente["id"], "servico_id": 999, "data_hora": DIA_20_MANHA},
        headers=auth_headers,

    )

    assert sem_cliente.status_code == 404
    assert sem_servico.status_code == 404


def test_servico_desativado_nao_pode_ser_agendado(
        
    client: TestClient, auth_headers: dict

):
    
    cliente, servico = preparar(client, auth_headers)
    client.delete(f"/servicos/{servico['id']}", headers=auth_headers)

    resposta = client.post(

        "/agendamentos",
        json={

            "cliente_id": cliente["id"],
            "servico_id": servico["id"],
            "data_hora": DIA_20_MANHA,

        },

        headers=auth_headers,

    )

    assert resposta.status_code == 404


def test_nao_agenda_com_cliente_ou_servico_de_outra_barbearia(client: TestClient):

    headers_a = registrar_e_logar(client, "a@email.com", "Barbearia A")
    headers_b = registrar_e_logar(client, "b@email.com", "Barbearia B")
    cliente_a, servico_a = preparar(client, headers_a)
    cliente_b, servico_b = preparar(client, headers_b)

    cliente_alheio = client.post(

        "/agendamentos",
        json={

            "cliente_id": cliente_a["id"],
            "servico_id": servico_b["id"],
            "data_hora": DIA_20_MANHA,

        },

        headers=headers_b,

    )

    servico_alheio = client.post(

        "/agendamentos",
        json={

            "cliente_id": cliente_b["id"],
            "servico_id": servico_a["id"],
            "data_hora": DIA_20_MANHA,

        },

        headers=headers_b,

    )

    assert cliente_alheio.status_code == 404
    assert servico_alheio.status_code == 404


def test_dados_invalidos_retornam_422(client: TestClient, auth_headers: dict):

    resposta = client.post(

        "/agendamentos",
        json={"cliente_id": 1, "servico_id": 1, "data_hora": "ontem a tarde"},
        headers=auth_headers,

    )

    assert resposta.status_code == 422


def test_listar_por_periodo_em_ordem_de_horario(
        
    client: TestClient, auth_headers: dict

):
    cliente, servico = preparar(client, auth_headers)
    tarde = criar_agendamento(

        client, auth_headers, cliente["id"], servico["id"], DIA_20_TARDE
        
    )

    manha = criar_agendamento(

        client, auth_headers, cliente["id"], servico["id"], DIA_20_MANHA

    )

    criar_agendamento(client, auth_headers, cliente["id"], servico["id"], DIA_21_MANHA)

    resposta = client.get(
        
        "/agendamentos",
        params={"inicio": "2026-10-20T00:00:00Z", "fim": "2026-10-21T00:00:00Z"},
        headers=auth_headers,

    )

    assert resposta.status_code == 200
    ids = [a["id"] for a in resposta.json()]
    assert ids == [manha["id"], tarde["id"]]


def test_listar_sem_filtro_traz_tudo(client: TestClient, auth_headers: dict):

    cliente, servico = preparar(client, auth_headers)
    criar_agendamento(client, auth_headers, cliente["id"], servico["id"], DIA_20_MANHA)
    criar_agendamento(client, auth_headers, cliente["id"], servico["id"], DIA_21_MANHA)

    resposta = client.get("/agendamentos", headers=auth_headers)

    assert len(resposta.json()) == 2


def test_periodo_invertido_retorna_400(client: TestClient, auth_headers: dict):

    resposta = client.get(

        "/agendamentos",
        params={"inicio": "2026-10-21T00:00:00Z", "fim": "2026-10-20T00:00:00Z"},
        headers=auth_headers,

    )

    assert resposta.status_code == 400


def test_filtrar_por_status_e_por_cliente(client: TestClient, auth_headers: dict):

    ana = criar_cliente(client, auth_headers, "Ana")
    bruno = criar_cliente(client, auth_headers, "Bruno")
    servico = criar_servico(client, auth_headers)
    da_ana = criar_agendamento(client, auth_headers, ana["id"], servico["id"])
    do_bruno = criar_agendamento(

        client, auth_headers, bruno["id"], servico["id"], DIA_21_MANHA

    )

    mudar_status(client, auth_headers, do_bruno["id"], "confirmado")

    confirmados = client.get(

        "/agendamentos", params={"status": "confirmado"}, headers=auth_headers

    ).json()

    historico_ana = client.get(

        "/agendamentos", params={"cliente_id": ana["id"]}, headers=auth_headers

    ).json()

    assert [a["id"] for a in confirmados] == [do_bruno["id"]]
    assert [a["id"] for a in historico_ana] == [da_ana["id"]]


def test_status_invalido_no_filtro_retorna_422(client: TestClient, auth_headers: dict):

    resposta = client.get(

        "/agendamentos", params={"status": "inventado"}, headers=auth_headers

    )

    assert resposta.status_code == 422


def test_reagendar_so_muda_a_data_e_preserva_o_resto(
        
    client: TestClient, auth_headers: dict

):
    
    cliente, servico = preparar(client, auth_headers)
    ag = criar_agendamento(client, auth_headers, cliente["id"], servico["id"])

    resposta = client.put(

        f"/agendamentos/{ag['id']}",
        json={"data_hora": DIA_21_MANHA},
        headers=auth_headers,

    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["data_hora"].startswith("2026-10-21T13:00:00")
    assert corpo["valor"] == 35.0
    assert corpo["cliente_id"] == cliente["id"]


def test_fluxo_normal_de_status(client: TestClient, auth_headers: dict):

    cliente, servico = preparar(client, auth_headers)
    ag = criar_agendamento(client, auth_headers, cliente["id"], servico["id"])

    confirmado = mudar_status(client, auth_headers, ag["id"], "confirmado")
    concluido = mudar_status(client, auth_headers, ag["id"], "concluido")

    assert confirmado.status_code == 200
    assert confirmado.json()["status"] == "confirmado"
    assert concluido.status_code == 200
    assert concluido.json()["status"] == "concluido"


def test_status_final_nao_muda_mais(client: TestClient, auth_headers: dict):

    cliente, servico = preparar(client, auth_headers)
    ag = criar_agendamento(client, auth_headers, cliente["id"], servico["id"])
    mudar_status(client, auth_headers, ag["id"], "concluido")

    voltar = mudar_status(client, auth_headers, ag["id"], "agendado")
    cancelar = mudar_status(client, auth_headers, ag["id"], "cancelado")
    reagendar = client.put(

        f"/agendamentos/{ag['id']}",
        json={"data_hora": DIA_21_MANHA},
        headers=auth_headers,

    )

    assert voltar.status_code == 409
    assert cancelar.status_code == 409
    assert reagendar.status_code == 409


def test_cancelar_agendamento(client: TestClient, auth_headers: dict):

    cliente, servico = preparar(client, auth_headers)
    ag = criar_agendamento(client, auth_headers, cliente["id"], servico["id"])

    resposta = mudar_status(client, auth_headers, ag["id"], "cancelado")

    assert resposta.status_code == 200
    assert resposta.json()["status"] == "cancelado"


def test_status_desconhecido_retorna_422(client: TestClient, auth_headers: dict):

    cliente, servico = preparar(client, auth_headers)
    ag = criar_agendamento(client, auth_headers, cliente["id"], servico["id"])

    resposta = mudar_status(client, auth_headers, ag["id"], "sumiu")

    assert resposta.status_code == 422


def test_agendamento_inexistente_retorna_404(client: TestClient, auth_headers: dict):

    assert client.get("/agendamentos/999", headers=auth_headers).status_code == 404
    assert mudar_status(client, auth_headers, 999, "confirmado").status_code == 404


def test_isolamento_entre_barbearias(client: TestClient):
    
    headers_a = registrar_e_logar(client, "a@email.com", "Barbearia A")
    headers_b = registrar_e_logar(client, "b@email.com", "Barbearia B")
    cliente, servico = preparar(client, headers_a)
    ag = criar_agendamento(client, headers_a, cliente["id"], servico["id"])
    url = f"/agendamentos/{ag['id']}"

    assert client.get("/agendamentos", headers=headers_b).json() == []
    assert client.get(url, headers=headers_b).status_code == 404
    assert client.put(url, json={"observacoes": "x"}, headers=headers_b).status_code == 404
    assert mudar_status(client, headers_b, ag["id"], "cancelado").status_code == 404

    intacto = client.get(url, headers=headers_a).json()
    assert intacto["status"] == "agendado"