from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from app.api.deps import get_current_user
from app.db.session import get_session
from app.models.usuario import Usuario
from app.schemas.financeiro import (

    CategoriaCreate,
    CategoriaRead,
    MovimentacaoCreate,
    MovimentacaoRead,
    ResumoFinanceiro,
    TipoFinanceiro,

)
from app.services import financeiro_service

router = APIRouter()


@router.post(
        
    "/categorias", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED

)
def criar_categoria(

    dados: CategoriaCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return financeiro_service.criar_categoria(session, usuario, dados)


@router.get("/categorias", response_model=list[CategoriaRead])
def listar_categorias(

    tipo: Optional[TipoFinanceiro] = None,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return financeiro_service.listar_categorias(session, usuario, tipo)


@router.post(
        
    "/movimentacoes",
    response_model=MovimentacaoRead,
    status_code=status.HTTP_201_CREATED,

)
def criar_movimentacao(

    dados: MovimentacaoCreate,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return financeiro_service.criar_movimentacao(session, usuario, dados)


@router.get("/movimentacoes", response_model=list[MovimentacaoRead])
def listar_movimentacoes(

    inicio: Optional[date] = None,
    fim: Optional[date] = None,
    tipo: Optional[TipoFinanceiro] = None,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return financeiro_service.listar_movimentacoes(session, usuario, inicio, fim, tipo)


@router.delete("/movimentacoes/{movimentacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_movimentacao(

    movimentacao_id: int,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    financeiro_service.deletar_movimentacao(session, usuario, movimentacao_id)


@router.get("/resumo", response_model=ResumoFinanceiro)
def resumo(

    inicio: Optional[date] = None,
    fim: Optional[date] = None,
    session: Session = Depends(get_session),
    usuario: Usuario = Depends(get_current_user),

):
    
    return financeiro_service.resumo(session, usuario, inicio, fim)