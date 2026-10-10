from sqlmodel import Session
from app.models.barbearia import Barbearia
from app.models.barbeiro import Barbeiro
from app.models.usuario import Usuario
from app.repositories import barbeiro_repository


def obter_barbeiro_padrao(
        
    session: Session, usuario: Usuario, barbearia: Barbearia

) -> Barbeiro:
    
    """No MVP o dono atende sozinho: usa o primeiro barbeiro ativo da barbearia
    e, se ainda nao existir, cria um para o proprio dono."""
    barbeiro = barbeiro_repository.buscar_ativo_por_barbearia(session, barbearia.id)
    if barbeiro is None:
        barbeiro = barbeiro_repository.criar(

            session, Barbeiro(usuario_id=usuario.id, barbearia_id=barbearia.id)

        )
        
    return barbeiro