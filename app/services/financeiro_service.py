from datetime import date, timedelta, timezone
from fastapi import HTTPException, status
from sqlmodel import Session
from app.models.agendamento import Agendamento
from app.models.barbearia import Barbearia
from app.models.categoria_financeira import CategoriaFinanceira
from app.models.financeiro import MovimentacaoFinanceira
from app.models.usuario import Usuario
from app.repositories import categoria_repository, movimentacao_repository
from app.schemas.financeiro import (

    CategoriaCreate,
    MovimentacaoCreate,
    ResumoFinanceiro,

)
from app.services.barbearia_service import obter_barbearia

# Fuso do negocio (Brasilia, UTC-3, sem horario de verao). Serve para decidir em que DIA do caixa a receita cai: um corte as 22h locais ja e "amanha" em UTC.
FUSO_NEGOCIO = timezone(timedelta(hours=-3))

CATEGORIA_SERVICOS = "Servicos"


def _nao_encontrado(recurso: str) -> HTTPException:

    return HTTPException(

        status_code=status.HTTP_404_NOT_FOUND, detail=f"{recurso} nao encontrada"

    )


def criar_categoria(
        
    session: Session, usuario: Usuario, dados: CategoriaCreate

) -> CategoriaFinanceira:
    
    barbearia = obter_barbearia(session, usuario)
    nome = dados.nome.strip()
    if categoria_repository.buscar_por_nome_e_tipo(

        session, barbearia.id, nome, dados.tipo

    ):
        
        raise HTTPException(

            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ja existe uma categoria de {dados.tipo} chamada '{nome}'",

        )
    
    return categoria_repository.criar(

        session,
        CategoriaFinanceira(barbearia_id=barbearia.id, nome=nome, tipo=dados.tipo),

    )


def listar_categorias(
        
    session: Session, usuario: Usuario, tipo: str | None

) -> list[CategoriaFinanceira]:
    
    barbearia = obter_barbearia(session, usuario)
    return categoria_repository.listar_por_barbearia(session, barbearia.id, tipo)


def _obter_categoria_servicos(
        
    session: Session, barbearia: Barbearia

) -> CategoriaFinanceira:
    
    """Categoria usada nas receitas automaticas; criada na primeira vez."""
    categoria = categoria_repository.buscar_por_nome_e_tipo(

        session, barbearia.id, CATEGORIA_SERVICOS, "receita"

    )

    if categoria is None:

        categoria = categoria_repository.criar(

            session,
            CategoriaFinanceira(

                barbearia_id=barbearia.id, nome=CATEGORIA_SERVICOS, tipo="receita"

            ),

        )

    return categoria


def registrar_receita_do_agendamento(
        
    session: Session, barbearia: Barbearia, agendamento: Agendamento

) -> MovimentacaoFinanceira:
    
    """Chamado quando o agendamento vira 'concluido'. Copia o valor congelado."""
    categoria = _obter_categoria_servicos(session, barbearia)
    momento = agendamento.data_hora
    if momento.tzinfo is None:  # alguns bancos devolvem sem fuso; guardamos em UTC

        momento = momento.replace(tzinfo=timezone.utc)

    data_local = momento.astimezone(FUSO_NEGOCIO).date()
    return movimentacao_repository.criar(

        session,
        MovimentacaoFinanceira(

            barbearia_id=barbearia.id,
            tipo="receita",
            categoria_id=categoria.id,
            descricao=f"Atendimento #{agendamento.id}",
            valor=agendamento.valor,
            data=data_local,
            agendamento_id=agendamento.id,

        ),

    )


def criar_movimentacao(
        
    session: Session, usuario: Usuario, dados: MovimentacaoCreate

) -> MovimentacaoFinanceira:
    
    barbearia = obter_barbearia(session, usuario)
    categoria = categoria_repository.buscar_por_id(session, dados.categoria_id)
    if categoria is None or categoria.barbearia_id != barbearia.id:

        raise _nao_encontrado("Categoria")
    
    if categoria.tipo != dados.tipo:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(

                f"A categoria '{categoria.nome}' e de {categoria.tipo}, "
                f"nao pode ser usada em uma {dados.tipo}"

            ),

        )
    
    return movimentacao_repository.criar(

        session,
        MovimentacaoFinanceira(

            barbearia_id=barbearia.id,
            tipo=dados.tipo,
            categoria_id=categoria.id,
            descricao=dados.descricao,
            valor=dados.valor,
            data=dados.data,

        ),

    )


def _validar_periodo(inicio: date | None, fim: date | None) -> None:

    if inicio is not None and fim is not None and inicio > fim:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'inicio' nao pode ser depois de 'fim'",

        )


def listar_movimentacoes(
        
    session: Session,
    usuario: Usuario,
    inicio: date | None,
    fim: date | None,
    tipo: str | None,

) -> list[MovimentacaoFinanceira]:
    
    barbearia = obter_barbearia(session, usuario)
    _validar_periodo(inicio, fim)
    return movimentacao_repository.listar(session, barbearia.id, inicio, fim, tipo)


def deletar_movimentacao(
        
    session: Session, usuario: Usuario, movimentacao_id: int

) -> None:
    
    barbearia = obter_barbearia(session, usuario)
    mov = movimentacao_repository.buscar_por_id(session, movimentacao_id)
    if mov is None or mov.barbearia_id != barbearia.id:

        raise _nao_encontrado("Movimentacao")
    
    if mov.agendamento_id is not None:

        raise HTTPException(

            status_code=status.HTTP_409_CONFLICT,
            detail="Receita gerada por um atendimento nao pode ser excluida",

        )
    
    movimentacao_repository.deletar(session, mov)


def resumo(
        
    session: Session, usuario: Usuario, inicio: date | None, fim: date | None

) -> ResumoFinanceiro:
    
    barbearia = obter_barbearia(session, usuario)
    _validar_periodo(inicio, fim)
    movs = movimentacao_repository.listar(session, barbearia.id, inicio, fim)
    receitas = round(sum(m.valor for m in movs if m.tipo == "receita"), 2)
    despesas = round(sum(m.valor for m in movs if m.tipo == "despesa"), 2)
    return ResumoFinanceiro(

        inicio=inicio,
        fim=fim,
        receitas=receitas,
        despesas=despesas,
        saldo=round(receitas - despesas, 2),
        quantidade=len(movs),
        
    )