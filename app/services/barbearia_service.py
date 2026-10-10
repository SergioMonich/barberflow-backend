from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.barbearia import Barbearia
from app.models.usuario import Usuario
from app.repositories import barbearia_repository


def obter_barbearia(session: Session, usuario: Usuario) -> Barbearia:

    barbearia = barbearia_repository.buscar_por_dono(session, usuario.id)
    if barbearia is None:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario nao possui barbearia cadastrada",

        )
    
    return barbearia