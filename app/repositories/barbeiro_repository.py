from sqlmodel import Session, select
from app.models.barbeiro import Barbeiro


def buscar_ativo_por_barbearia(session: Session, barbearia_id: int) -> Barbeiro | None:

    statement = (

        select(Barbeiro)
        .where(Barbeiro.barbearia_id == barbearia_id)
        .where(Barbeiro.ativo == True)  # noqa: E712
        .order_by(Barbeiro.id)

    )

    return session.exec(statement).first()


def criar(session: Session, barbeiro: Barbeiro) -> Barbeiro:
    
    session.add(barbeiro)
    session.commit()
    session.refresh(barbeiro)
    return barbeiro