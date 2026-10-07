from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteCreate, ClienteRead, ClienteUpdate
from app.services import cliente_service

router = APIRouter()


@router.post("", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
def criar_cliente(

    dados: ClienteCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return cliente_service.criar_cliente(session, usuario, dados)


@router.get("", response_model=list[ClienteRead])
def listar_clientes(

    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return cliente_service.listar_clientes(session, usuario)


@router.get("/{cliente_id}", response_model=ClienteRead)
def buscar_cliente(

    cliente_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return cliente_service.buscar_cliente(session, usuario, cliente_id)


@router.put("/{cliente_id}", response_model=ClienteRead)
def atualizar_cliente(

    cliente_id: int,
    dados: ClienteUpdate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return cliente_service.atualizar_cliente(session, usuario, cliente_id, dados)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(

    cliente_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),
    
):
    
    cliente_service.deletar_cliente(session, usuario, cliente_id)