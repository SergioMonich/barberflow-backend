from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.usuario import Usuario
from app.schemas.agendamento import (

    AgendamentoCreate,
    AgendamentoRead,
    AgendamentoUpdate,
    StatusAgendamento,
    StatusUpdate,

)
from app.services import agendamento_service

router = APIRouter()


@router.post("", response_model=AgendamentoRead, status_code=status.HTTP_201_CREATED)
def criar_agendamento(

    dados: AgendamentoCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return agendamento_service.criar_agendamento(session, usuario, dados)


@router.get("", response_model=list[AgendamentoRead])
def listar_agendamentos(

    inicio: Optional[datetime] = None,
    fim: Optional[datetime] = None,
    status_agendamento: Optional[StatusAgendamento] = Query(default=None, alias="status"),
    cliente_id: Optional[int] = None,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return agendamento_service.listar_agendamentos(

        session, usuario, inicio, fim, status_agendamento, cliente_id

    )


@router.get("/{agendamento_id}", response_model=AgendamentoRead)
def buscar_agendamento(

    agendamento_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return agendamento_service.buscar_agendamento(session, usuario, agendamento_id)


@router.put("/{agendamento_id}", response_model=AgendamentoRead)
def atualizar_agendamento(

    agendamento_id: int,
    dados: AgendamentoUpdate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return agendamento_service.atualizar_agendamento(

        session, usuario, agendamento_id, dados

    )


@router.patch("/{agendamento_id}/status", response_model=AgendamentoRead)
def alterar_status(

    agendamento_id: int,
    dados: StatusUpdate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return agendamento_service.alterar_status(

        session, usuario, agendamento_id, dados.status
        
    )