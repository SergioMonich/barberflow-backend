# BarberFlow Backend — Guia da Etapa 6 (CRUD de Clientes)

Bem-vindo ao projeto! Este documento tem tudo que você precisa para implementar o CRUD de Clientes sem precisar entender o projeto inteiro de uma vez.

## 1. O que é o projeto

API FastAPI para um app de gestão de barbearias (agenda + financeiro básico). Backend em Python, banco PostgreSQL, ORM SQLModel.

## 2. Como rodar o projeto na sua máquina

```bash
git clone https://github.com/SergioMonich/barberflow-backend.git
cd barberflow-backend
git checkout etapa-6-clientes

python -m venv venv
source venv/Scripts/activate        # Windows (Git Bash)
# ou: source venv/bin/activate      # Linux/Mac

pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha com os valores do seu Postgres local (veja a seção 3).

Suba um Postgres local via Docker (ajuste a porta se 5432 já estiver ocupada na sua máquina):

```bash
docker run --name barberflow-db \
  -e POSTGRES_USER=barberflow \
  -e POSTGRES_PASSWORD=barberflow123 \
  -e POSTGRES_DB=barberflow \
  -p 5432:5432 \
  -v barberflow-data:/var/lib/postgresql/data \
  -d postgres:16
```

Rode o servidor:

```bash
uvicorn app.main:app --reload
```

As 8 tabelas são criadas automaticamente ao subir o servidor (ver `app/db/init_db.py`). Teste em `http://127.0.0.1:8000/docs`.

## 3. Arquivo `.env` necessário

```
DATABASE_URL=postgresql+psycopg://barberflow:barberflow123@localhost:5432/barberflow
SECRET_KEY=gere-a-sua-com-python -c "import secrets; print(secrets.token_hex(32))"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

## 4. Arquitetura do projeto (importante seguir o padrão)

```
Router (recebe a requisição)
   ↓
Service (regra de negócio)
   ↓
Repository (acesso ao banco)
   ↓
Model (SQLModel = tabela)
```

Cada camada só conhece a camada logo abaixo dela. O Router nunca fala direto com o banco — sempre passa pelo Service, que passa pelo Repository.

**Use o módulo de autenticação (`app/api/routers/auth.py`, `app/services/auth_service.py`, `app/repositories/usuario_repository.py`) como modelo/referência** — ele já segue exatamente esse padrão e é o exemplo mais completo que existe no projeto até agora.

## 5. O que você vai construir

### Model já existe — `app/models/cliente.py`
```python
class Cliente(SQLModel, table=True):
    id: Optional[int]
    barbearia_id: int       # FK → Barbearia
    nome: str                # obrigatório
    telefone: Optional[str]
    email: Optional[str]
    observacoes: Optional[str]
    criado_em: datetime
```

### Arquivos a criar

**`app/schemas/cliente.py`**
- `ClienteCreate`: nome (obrigatório), telefone, email, observacoes — sem `id`, sem `barbearia_id` (isso vem do usuário logado, não do corpo da requisição).
- `ClienteRead`: todos os campos, incluindo `id` e `barbearia_id` — é o que a API devolve.
- `ClienteUpdate`: todos os campos opcionais (permite atualizar só o que for enviado).

**`app/repositories/cliente_repository.py`**
Funções simples, recebendo `session: Session` como primeiro parâmetro:
- `criar(session, cliente: Cliente) -> Cliente`
- `buscar_por_id(session, cliente_id: int) -> Cliente | None`
- `listar_por_barbearia(session, barbearia_id: int) -> list[Cliente]`
- `atualizar(session, cliente: Cliente) -> Cliente`
- `deletar(session, cliente: Cliente) -> None`

**`app/services/cliente_service.py`**
Regras de negócio, por exemplo:
- Ao criar, associa automaticamente o `barbearia_id` do usuário logado (nunca confie num `barbearia_id` vindo do corpo da requisição — isso seria uma falha de segurança, permitindo um usuário mexer em dados de outra barbearia).
- Ao buscar/atualizar/deletar por `id`, confirme que o cliente pertence à barbearia do usuário logado antes de agir — senão devolva 404 (não 403, para não revelar que o registro existe em outra conta).

**`app/api/routers/clientes.py`**
Endpoints (todos protegidos — exigem login, use a mesma dependência `get_current_user` que a Etapa 5 criou):

| Método | Rota | Entrada | Retorno |
|--------|------|---------|---------|
| POST | `/clientes` | `ClienteCreate` | `ClienteRead`, 201 |
| GET | `/clientes` | — | lista de `ClienteRead` |
| GET | `/clientes/{id}` | — | `ClienteRead`, 404 se não existir/não for seu |
| PUT | `/clientes/{id}` | `ClienteUpdate` | `ClienteRead` |
| DELETE | `/clientes/{id}` | — | 204 (sem corpo) |

Por fim, registre o router em `app/main.py`:
```python
app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
```

## 6. Como testar

Pelo Swagger (`/docs`): registre um usuário, faça login, clique em **Authorize** e cole o token, depois teste as rotas de clientes direto pela interface.

## 7. Git

Está tudo na branch `etapa-6-clientes` — comite ali, não direto na `main`. Quando terminar, abra um Pull Request para revisão antes de fazer o merge.

## 8. Dúvidas

Se travar em algo, descreva o erro completo (a mensagem toda, não só um resumo) — isso ajuda demais a diagnosticar rápido.
