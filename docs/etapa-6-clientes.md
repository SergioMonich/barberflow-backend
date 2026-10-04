# BarberFlow Backend — Guia da Etapa 6 (CRUD de Clientes)

Bem-vindo ao projeto! Este documento tem tudo que você precisa para implementar o CRUD de Clientes sem precisar entender o projeto inteiro de uma vez — incluindo o contexto e as decisões que vieram antes de você entrar, já que elas não estão em nenhuma outra conversa que você tenha acesso.

## 1. O que é o projeto

API FastAPI para um app de gestão de barbearias (agenda + financeiro básico), voltado para barbeiros autônomos e pequenas barbearias que hoje controlam tudo por WhatsApp/caderno. Backend em Python, banco PostgreSQL, ORM SQLModel. Também é um trabalho acadêmico (exige CRUD completo, JWT, Swagger e uma camada de repositories).

## 1.1 Decisões de arquitetura e o porquê (leia antes de codar)

- **Toda tabela tem `barbearia_id`**, mesmo o MVP sendo de 1 barbearia por usuário. Isso é proposital: prepara o sistema para "múltiplos barbeiros/barbearias" no futuro sem reescrever o banco. Por isso, **nunca confie num `barbearia_id` vindo do corpo da requisição** — sempre pegue do usuário logado.
- **Padrão de 3 camadas obrigatório**: Router → Service → Repository → Model. Não pule camadas (ex: Router nunca chama o banco direto). Veja a seção 4.
- **Campos de valor "congelados"**: em `Agendamento.valor` e `MovimentacaoFinanceira.valor`, o número é copiado no momento da criação, não uma referência viva ao preço atual do serviço. Isso existe para que mudanças de preço no futuro não alterem retroativamente relatórios financeiros antigos. Não é redundância — é proposital. (Isso não afeta diretamente o CRUD de Clientes, mas ajuda a entender o estilo de modelagem do projeto.)
- **Erros de rota protegida devolvem 404, não 403** quando o registro existe mas pertence a outra barbearia — isso evita vazar a informação de que o registro existe.

## 1.2 Entidades do banco (visão completa, não só Cliente)

| Entidade | O que guarda |
|----------|--------------|
| Usuario | login/senha, dono da conta |
| Barbearia | 1 por usuário dono (no MVP) |
| Barbeiro | pode ser o próprio dono, no MVP |
| **Cliente** | **← você vai trabalhar aqui** |
| Servico | nome, preço, duração |
| Agendamento | liga cliente + barbeiro + serviço + data |
| CategoriaFinanceira | categoriza receitas/despesas |
| MovimentacaoFinanceira | receitas e despesas, pode vir de um agendamento concluído |

Nenhuma dessas outras entidades tem rotas (Router/Service/Repository) prontas ainda além de `Usuario` (autenticação) — só os models/tabelas existem.

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

## 8. Problemas já conhecidos (para não perder tempo redescobrindo)

- **Pydantic v2**: `class Config: env_file = ".env"` dentro de uma classe de Settings **não funciona mais** — use `model_config = SettingsConfigDict(env_file=".env")`.
- **psycopg2 no Windows**: se aparecer `UnicodeDecodeError: 'utf-8' codec can't decode byte ...` ao conectar no banco, é um bug conhecido do psycopg2 em máquinas Windows com idioma português — o projeto já usa `psycopg` (v3) em vez de `psycopg2-binary` por causa disso. Se por algum motivo isso reaparecer, o erro real costuma estar escondido atrás desse erro de Unicode.
- **Porta 5432 ocupada**: se você já tiver um PostgreSQL instalado nativamente no Windows, ele pode brigar pela porta 5432 com o container Docker. Nesse caso, suba o container numa porta diferente (ex: `-p 5433:5432`) e ajuste o `DATABASE_URL` no seu `.env` — isso é só local, não precisa avisar ninguém nem mudar nada no código.
- **Colar código no VS Code**: preste atenção se o editor não "achatar" o código em uma linha só ao colar (aconteceu bastante durante o desenvolvimento). Python é sensível a indentação — confira sempre antes de salvar.

## 9. Dúvidas

Se travar em algo, descreva o erro completo (a mensagem toda, não só um resumo) — isso ajuda demais a diagnosticar rápido.
