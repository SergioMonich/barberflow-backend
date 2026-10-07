from sqlmodel import Session, select 
from app.models.barbearia import Barbearia 

#Precisamos disso porque Usuario não tem barbearia_id diretamente, é Barbearia que aponta pro dono (dono_id). Então, pra saber a barbearia do usuário logado, buscamos pela relação inversa
def buscar_por_dono(session: Session, dono_id: int) -> Barbearia | None: 

    statement = select(Barbearia).where(Barbearia.dono_id == dono_id) 
    
    return session.exec(statement).first()


def criar(session: Session, barbearia: Barbearia) -> Barbearia: 
    
    session.add(barbearia) 
    session.commit() 
    session.refresh(barbearia) 
    
    return barbearia