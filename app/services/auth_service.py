from fastapi import HTTPException, status
from sqlmodel import Session
from app.core.security import hash_senha, verificar_senha
from app.models.barbearia import Barbearia
from app.models.usuario import Usuario
from app.repositories import barbearia_repository, usuario_repository
from app.schemas.usuario import UsuarioCreate


def registrar_usuario(session: Session, dados: UsuarioCreate) -> Usuario:

    usuario_existente = usuario_repository.buscar_por_email(session, dados.email)
    if usuario_existente:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ja cadastrado",
        )

    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=hash_senha(dados.senha),
    )

    usuario_criado = usuario_repository.criar(session, novo_usuario)

    nova_barbearia = Barbearia(
        nome=dados.nome_barbearia,
        dono_id=usuario_criado.id,
    )
    
    barbearia_repository.criar(session, nova_barbearia)

    return usuario_criado


def autenticar_usuario(session: Session, email: str, senha: str) -> Usuario:

    usuario = usuario_repository.buscar_por_email(session, email)
    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos", #boa pratica: mesma mensagem para email inexistente e senha errada, evita que alguém descubra quais emails já estão cadastrados.
        )

    return usuario