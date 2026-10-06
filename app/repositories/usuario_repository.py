from sqlmodel import Session, select 
from app.models.usuario import Usuario 

#"""buscar_por_email usa select(...).where(...) que é a forma do SQLModel de montar um SELECT ... WHERE. first() pega o primeiro resultado ou None se não achar nada (útil pra checar se o email já existe antes de criar)"""
def buscar_por_email(session: Session, email: str) -> Usuario | None: 
    
    statement = select(Usuario).where(Usuario.email == email) 
    return session.exec(statement).first() 

#"""add coloca o objeto na sessão, commit salva de verdade no banco, e refresh atualiza o objeto Python com o que o banco gerou (como o id, que só existe depois do INSERT)"""
def criar(session: Session, usuario: Usuario) -> Usuario:
     
    session.add(usuario) 
    session.commit() 
    session.refresh(usuario) 
    
    return usuario