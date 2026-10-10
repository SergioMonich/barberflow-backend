from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.barbearia import Barbearia
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from app.repositories import barbearia_repository, cliente_repository
from app.schemas.cliente import ClienteCreate, ClienteUpdate
from app.services.barbearia_service import obter_barbearia


def _obter_cliente_da_barbearia(session: Session, usuario: Usuario, cliente_id: int) -> Cliente:

    barbearia = obter_barbearia(session, usuario)
    cliente = cliente_repository.buscar_por_id(session, cliente_id)

    if cliente is None or cliente.barbearia_id != barbearia.id:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente nao encontrado", #404 tanto se nao existe quanto se pertence a outra barbearia evita revelar que o registro existe na conta de outra pessoa.
        )
    
    return cliente


def criar_cliente(session: Session, usuario: Usuario, dados: ClienteCreate) -> Cliente:

    barbearia = obter_barbearia(session, usuario)
    novo_cliente = Cliente(

        barbearia_id=barbearia.id,
        nome=dados.nome,
        telefone=dados.telefone,
        email=dados.email,
        observacoes=dados.observacoes,

    )

    return cliente_repository.criar(session, novo_cliente)


def listar_clientes(session: Session, usuario: Usuario) -> list[Cliente]:

    barbearia = obter_barbearia(session, usuario)

    return cliente_repository.listar_por_barbearia(session, barbearia.id)


def buscar_cliente(session: Session, usuario: Usuario, cliente_id: int) -> Cliente:

    return _obter_cliente_da_barbearia(session, usuario, cliente_id)


def atualizar_cliente(session: Session, usuario: Usuario, cliente_id: int, dados: ClienteUpdate) -> Cliente:

    cliente = _obter_cliente_da_barbearia(session, usuario, cliente_id)
    
    campos_enviados = dados.model_dump(exclude_unset=True) #model_dump(exclude_unset=True) pega só os campos que o cliente da API realmente enviou, permitindo atualizar só o telefone, por exemplo, sem apagar o resto
    for campo, valor in campos_enviados.items():

        setattr(cliente, campo, valor)

    return cliente_repository.atualizar(session, cliente)


def deletar_cliente(session: Session, usuario: Usuario, cliente_id: int) -> None:

    cliente = _obter_cliente_da_barbearia(session, usuario, cliente_id)
    cliente_repository.deletar(session, cliente)