from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.servico import Servico
from app.models.usuario import Usuario
from app.repositories import servico_repository
from app.schemas.servico import ServicoCreate, ServicoUpdate
from app.services.barbearia_service import obter_barbearia


def _obter_servico_da_barbearia(
        
    session: Session, usuario: Usuario, servico_id: int

) -> Servico:
    
    barbearia = obter_barbearia(session, usuario)
    servico = servico_repository.buscar_por_id(session, servico_id)

    # 404 tambem para servico de outra barbearia ou ja desativado.
    if servico is None or servico.barbearia_id != barbearia.id or not servico.ativo:
        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,
            detail="Servico nao encontrado",

        )
    
    return servico


def criar_servico(session: Session, usuario: Usuario, dados: ServicoCreate) -> Servico:

    barbearia = obter_barbearia(session, usuario)
    novo = Servico(

        barbearia_id=barbearia.id,
        nome=dados.nome,
        descricao=dados.descricao,
        preco=dados.preco,
        duracao_minutos=dados.duracao_minutos,

    )

    return servico_repository.criar(session, novo)


def listar_servicos(session: Session, usuario: Usuario) -> list[Servico]:

    barbearia = obter_barbearia(session, usuario)
    return servico_repository.listar_ativos_por_barbearia(session, barbearia.id)


def buscar_servico(session: Session, usuario: Usuario, servico_id: int) -> Servico:

    return _obter_servico_da_barbearia(session, usuario, servico_id)


def atualizar_servico(
        
    session: Session, usuario: Usuario, servico_id: int, dados: ServicoUpdate

) -> Servico:
    
    servico = _obter_servico_da_barbearia(session, usuario, servico_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():

        setattr(servico, campo, valor)

    return servico_repository.atualizar(session, servico)


def desativar_servico(session: Session, usuario: Usuario, servico_id: int) -> None:
    
    servico = _obter_servico_da_barbearia(session, usuario, servico_id)
    servico.ativo = False
    servico_repository.atualizar(session, servico)