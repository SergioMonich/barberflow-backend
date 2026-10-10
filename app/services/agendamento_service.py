from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.agendamento import Agendamento
from app.models.barbearia import Barbearia
from app.models.cliente import Cliente
from app.models.servico import Servico
from app.models.usuario import Usuario
from app.repositories import (

    agendamento_repository,
    cliente_repository,
    servico_repository,

)
from app.schemas.agendamento import AgendamentoCreate, AgendamentoUpdate
from app.services import barbeiro_service
from app.services.barbearia_service import obter_barbearia

# Quais mudancas de status sao permitidas. Status finais nao saem do lugar.
TRANSICOES: dict[str, set[str]] = {

    "agendado": {"confirmado", "concluido", "cancelado", "nao_compareceu"},
    "confirmado": {"concluido", "cancelado", "nao_compareceu"},
    "concluido": set(),
    "cancelado": set(),
    "nao_compareceu": set(),

}

STATUS_EDITAVEIS = {"agendado", "confirmado"}


def _para_utc(valor: datetime) -> datetime:
    
    """Tudo e guardado em UTC. Datas sem fuso sao tratadas como UTC."""
    if valor.tzinfo is None:

        return valor.replace(tzinfo=timezone.utc)
    
    return valor.astimezone(timezone.utc)


def _nao_encontrado(recurso: str) -> HTTPException:

    return HTTPException(

        status_code=status.HTTP_404_NOT_FOUND, detail=f"{recurso} nao encontrado"

    )


def _obter_cliente(session: Session, barbearia: Barbearia, cliente_id: int) -> Cliente:

    cliente = cliente_repository.buscar_por_id(session, cliente_id)
    if cliente is None or cliente.barbearia_id != barbearia.id:

        raise _nao_encontrado("Cliente")
    
    return cliente


def _obter_servico_ativo(
        
    session: Session, barbearia: Barbearia, servico_id: int

) -> Servico:
    
    servico = servico_repository.buscar_por_id(session, servico_id)
    if servico is None or servico.barbearia_id != barbearia.id or not servico.ativo:

        raise _nao_encontrado("Servico")
    
    return servico


def _obter_agendamento_da_barbearia(
        
    session: Session, usuario: Usuario, agendamento_id: int

) -> Agendamento:
    
    barbearia = obter_barbearia(session, usuario)
    agendamento = agendamento_repository.buscar_por_id(session, agendamento_id)
    if agendamento is None or agendamento.barbearia_id != barbearia.id:

        raise _nao_encontrado("Agendamento")
    
    return agendamento


def criar_agendamento(
        
    session: Session, usuario: Usuario, dados: AgendamentoCreate

) -> Agendamento:
    
    barbearia = obter_barbearia(session, usuario)
    cliente = _obter_cliente(session, barbearia, dados.cliente_id)
    servico = _obter_servico_ativo(session, barbearia, dados.servico_id)
    barbeiro = barbeiro_service.obter_barbeiro_padrao(session, usuario, barbearia)

    novo = Agendamento(

        barbearia_id=barbearia.id,
        barbeiro_id=barbeiro.id,
        cliente_id=cliente.id,
        servico_id=servico.id,
        data_hora=_para_utc(dados.data_hora),
        # "Foto" do preco no momento: mudar o preco do servico depois
        # nao altera agendamentos ja criados.
        valor=servico.preco,
        observacoes=dados.observacoes,

    )

    return agendamento_repository.criar(session, novo)


def listar_agendamentos(
        
    session: Session,
    usuario: Usuario,
    inicio: datetime | None,
    fim: datetime | None,
    status_filtro: str | None,
    cliente_id: int | None,

) -> list[Agendamento]:
    
    barbearia = obter_barbearia(session, usuario)
    if inicio is not None:

        inicio = _para_utc(inicio)

    if fim is not None:

        fim = _para_utc(fim)

    if inicio is not None and fim is not None and inicio >= fim:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'inicio' deve ser anterior a 'fim'",

        )
    
    return agendamento_repository.listar(
        session, barbearia.id, inicio, fim, status_filtro, cliente_id

    )


def buscar_agendamento(
        
    session: Session, usuario: Usuario, agendamento_id: int

) -> Agendamento:
    
    return _obter_agendamento_da_barbearia(session, usuario, agendamento_id)


def atualizar_agendamento(
        
    session: Session, usuario: Usuario, agendamento_id: int, dados: AgendamentoUpdate

) -> Agendamento:
    
    agendamento = _obter_agendamento_da_barbearia(session, usuario, agendamento_id)
    if agendamento.status not in STATUS_EDITAVEIS:

        raise HTTPException(

            status_code=status.HTTP_409_CONFLICT,

            detail=f"Agendamento '{agendamento.status}' nao pode mais ser alterado",

        )

    campos = dados.model_dump(exclude_unset=True)
    if campos.get("data_hora") is None:

        campos.pop("data_hora", None)  # data_hora nao pode ficar vazia

    else:

        campos["data_hora"] = _para_utc(campos["data_hora"])


    for campo, valor in campos.items():

        setattr(agendamento, campo, valor)

    return agendamento_repository.atualizar(session, agendamento)


def alterar_status(
        
    session: Session, usuario: Usuario, agendamento_id: int, novo_status: str

) -> Agendamento:
    
    agendamento = _obter_agendamento_da_barbearia(session, usuario, agendamento_id)

    if novo_status not in TRANSICOES.get(agendamento.status, set()):

        raise HTTPException(

            status_code=status.HTTP_409_CONFLICT,
            detail=(

                f"Nao e possivel mudar de '{agendamento.status}' para '{novo_status}'"

            ),
            
        )

    agendamento.status = novo_status
    # Etapa 9 (Financeiro): ao virar "concluido", gerar a receita aqui.
    return agendamento_repository.atualizar(session, agendamento)