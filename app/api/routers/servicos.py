from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.usuario import Usuario
from app.schemas.servico import ServicoCreate, ServicoRead, ServicoUpdate
from app.services import servico_service

router = APIRouter()


@router.post("", response_model=ServicoRead, status_code=status.HTTP_201_CREATED)
def criar_servico(

    dados: ServicoCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return servico_service.criar_servico(session, usuario, dados)


@router.get("", response_model=list[ServicoRead])
def listar_servicos(

    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return servico_service.listar_servicos(session, usuario)


@router.get("/{servico_id}", response_model=ServicoRead)
def buscar_servico(

    servico_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return servico_service.buscar_servico(session, usuario, servico_id)


@router.put("/{servico_id}", response_model=ServicoRead)
def atualizar_servico(

    servico_id: int,
    dados: ServicoUpdate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return servico_service.atualizar_servico(session, usuario, servico_id, dados)


@router.delete("/{servico_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar_servico(

    servico_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),
):
    
    servico_service.desativar_servico(session, usuario, servico_id)