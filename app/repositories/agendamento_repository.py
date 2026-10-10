from datetime import datetime
from sqlmodel import Session, select
from app.models.agendamento import Agendamento


def criar(session: Session, agendamento: Agendamento) -> Agendamento:

    session.add(agendamento)
    session.commit()
    session.refresh(agendamento)
    return agendamento


def buscar_por_id(session: Session, agendamento_id: int) -> Agendamento | None:

    return session.get(Agendamento, agendamento_id)


def listar(
        
    session: Session,
    barbearia_id: int,
    inicio: datetime | None = None,
    fim: datetime | None = None,
    status: str | None = None,
    cliente_id: int | None = None,

) -> list[Agendamento]:
    
    statement = select(Agendamento).where(Agendamento.barbearia_id == barbearia_id)
    if inicio is not None:
        statement = statement.where(Agendamento.data_hora >= inicio)
    if fim is not None:
        statement = statement.where(Agendamento.data_hora < fim)
    if status is not None:
        statement = statement.where(Agendamento.status == status)
    if cliente_id is not None:
        statement = statement.where(Agendamento.cliente_id == cliente_id)
    statement = statement.order_by(Agendamento.data_hora)
    return list(session.exec(statement).all())


def atualizar(session: Session, agendamento: Agendamento) -> Agendamento:
    
    session.add(agendamento)
    session.commit()
    session.refresh(agendamento)
    return agendamento