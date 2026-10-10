from sqlmodel import Session, select
from app.models.categoria_financeira import CategoriaFinanceira


def criar(session: Session, categoria: CategoriaFinanceira) -> CategoriaFinanceira:

    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


def buscar_por_id(session: Session, categoria_id: int) -> CategoriaFinanceira | None:

    return session.get(CategoriaFinanceira, categoria_id)


def buscar_por_nome_e_tipo(
        
    session: Session, barbearia_id: int, nome: str, tipo: str

) -> CategoriaFinanceira | None:
    
    statement = (

        select(CategoriaFinanceira)
        .where(CategoriaFinanceira.barbearia_id == barbearia_id)
        .where(CategoriaFinanceira.nome == nome)
        .where(CategoriaFinanceira.tipo == tipo)

    )

    return session.exec(statement).first()


def listar_por_barbearia(
        
    session: Session, barbearia_id: int, tipo: str | None = None

) -> list[CategoriaFinanceira]:
    
    statement = select(CategoriaFinanceira).where(

        CategoriaFinanceira.barbearia_id == barbearia_id

    )

    if tipo is not None:

        statement = statement.where(CategoriaFinanceira.tipo == tipo)
        
    statement = statement.order_by(CategoriaFinanceira.nome)
    return list(session.exec(statement).all())