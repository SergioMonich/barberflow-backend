from datetime import date
from sqlmodel import Session, select
from app.models.financeiro import MovimentacaoFinanceira


def criar(
        
    session: Session, movimentacao: MovimentacaoFinanceira

) -> MovimentacaoFinanceira:
    
    session.add(movimentacao)
    session.commit()
    session.refresh(movimentacao)
    return movimentacao


def buscar_por_id(
        
    session: Session, movimentacao_id: int

) -> MovimentacaoFinanceira | None:
    
    return session.get(MovimentacaoFinanceira, movimentacao_id)


def listar(
        
    session: Session,
    barbearia_id: int,
    inicio: date | None = None,
    fim: date | None = None,
    tipo: str | None = None,

) -> list[MovimentacaoFinanceira]:
    
    """Periodo inclusivo nas duas pontas (inicio <= data <= fim)."""
    statement = select(MovimentacaoFinanceira).where(

        MovimentacaoFinanceira.barbearia_id == barbearia_id

    )

    if inicio is not None:

        statement = statement.where(MovimentacaoFinanceira.data >= inicio)

    if fim is not None:

        statement = statement.where(MovimentacaoFinanceira.data <= fim)
        
    if tipo is not None:

        statement = statement.where(MovimentacaoFinanceira.tipo == tipo)
    statement = statement.order_by(

        MovimentacaoFinanceira.data, MovimentacaoFinanceira.id

    )

    return list(session.exec(statement).all())


def deletar(session: Session, movimentacao: MovimentacaoFinanceira) -> None:
    
    session.delete(movimentacao)
    session.commit()