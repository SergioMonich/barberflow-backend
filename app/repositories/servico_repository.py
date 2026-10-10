from sqlmodel import Session, select
from app.models.servico import Servico


def criar(session: Session, servico: Servico) -> Servico:

    session.add(servico)
    session.commit()
    session.refresh(servico)
    return servico


def buscar_por_id(session: Session, servico_id: int) -> Servico | None:

    return session.get(Servico, servico_id)


def listar_ativos_por_barbearia(session: Session, barbearia_id: int) -> list[Servico]:

    statement = (

        select(Servico)
        .where(Servico.barbearia_id == barbearia_id)
        .where(Servico.ativo == True)  # noqa: E712
        .order_by(Servico.nome)

    )
    
    return list(session.exec(statement).all())


def atualizar(session: Session, servico: Servico) -> Servico:

    session.add(servico)
    session.commit()
    session.refresh(servico)
    return servico