from sqlmodel import Session, select 
from app.models.cliente import Cliente 

def criar(session: Session, cliente: Cliente) -> Cliente: 
    
    session.add(cliente) 
    session.commit() 
    session.refresh(cliente) 
    
    return cliente 


#session.get(Cliente, cliente_id) é um atalho do SQLModel pra buscar por chave primária, mais direto que montar um select() pra isso
def buscar_por_id(session: Session, cliente_id: int) -> Cliente | None: 
    
    return session.get(Cliente, cliente_id) 


def listar_por_barbearia(session: Session, barbearia_id: int) -> list[Cliente]:

    statement = select(Cliente).where(Cliente.barbearia_id == barbearia_id) 
    
    return list(session.exec(statement).all()) 


#reusa a mesma lógica de criar porque, no SQLModel, você só muda os atributos do objeto Python e manda de novo pro add/commit, não existe um 'update' separado
def atualizar(session: Session, cliente: Cliente) -> Cliente: 
    
    session.add(cliente) 
    session.commit() 
    session.refresh(cliente) 
    
    return cliente 


def deletar(session: Session, cliente: Cliente) -> None: 
    session.delete(cliente) 
    session.commit()