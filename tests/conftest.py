import os

# IMPORTANTE: estas variaveis precisam ser definidas ANTES de importar o app.
# Variaveis de ambiente tem prioridade sobre o arquivo .env, entao os testes usam um banco SQLite em memoria e NUNCA encostam no Postgres
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "chave-secreta-apenas-para-testes"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import app.models  # noqa: F401  (registra as tabelas no SQLModel)
from app.db.session import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    """Banco novo e vazio (em memoria) para cada teste."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Cliente HTTP que usa o banco de teste no lugar do Postgres."""

    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    # Sem "with": nao dispara o lifespan (que tentaria criar tabelas no Postgres).
    yield TestClient(app)
    app.dependency_overrides.clear()


def registrar_e_logar(
    client: TestClient, email: str, nome_barbearia: str = "Barbearia Teste"
) -> dict:
    """Cria um usuario (com barbearia) e devolve o header Authorization pronto."""
    client.post(
        "/auth/registro",
        json={
            "nome": "Usuario Teste",
            "email": email,
            "senha": "senha123",
            "nome_barbearia": nome_barbearia,
        },
    )
    resposta = client.post(
        "/auth/login", data={"username": email, "password": "senha123"}
    )
    token = resposta.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client: TestClient) -> dict:
    return registrar_e_logar(client, "dono@email.com")