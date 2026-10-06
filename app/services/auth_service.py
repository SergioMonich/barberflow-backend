from fastapi import HTTPException, status 
from sqlmodel import Session 
from app.models.usuario import Usuario 
from app.schemas.usuario import UsuarioCreate 
from app.repositories import usuario_repository 
from app.core.security import hash_senha, verificar_senha 

def registrar_usuario(session: Session, dados: UsuarioCreate) -> Usuario:

    usuario_existente = usuario_repository.buscar_por_email(session, dados.email) 
    if usuario_existente: raise HTTPException( status_code=status.HTTP_400_BAD_REQUEST, detail="Email ja cadastrado", ) 
    novo_usuario = Usuario( nome=dados.nome, email=dados.email, senha_hash=hash_senha(dados.senha), ) 
    return usuario_repository.criar(session, novo_usuario) 

def autenticar_usuario(session: Session, email: str, senha: str) -> Usuario: 

    usuario = usuario_repository.buscar_por_email(session, email) 
    if not usuario or not verificar_senha(senha, usuario.senha_hash): raise HTTPException( status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos", )
    #""""boa pratica: a mensagem de erro é a mesma ('Email ou senha incorretos') tanto se o email não existir quanto se a senha estiver errada — isso evita que alguém descubra, tentando emails aleatórios, quais já estão cadastrados no sistema""" 
    return usuario