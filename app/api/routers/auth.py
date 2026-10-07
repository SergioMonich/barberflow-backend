from fastapi import APIRouter, Depends 
from fastapi.security import OAuth2PasswordRequestForm 
from sqlmodel import Session 
from app.db.session import get_session 
from app.schemas.usuario import UsuarioCreate, UsuarioRead, Token 
from app.services import auth_service 
from app.core.security import criar_access_token
from app.api.deps import get_current_user
from app.models.usuario import Usuario  

router = APIRouter() 

@router.post("/registro", response_model=UsuarioRead, status_code=201) #response_model=UsuarioRead garante que a senha nunca aparece na resposta, mesmo que alguém esqueça de filtrar isso manualmente
def registrar(dados: UsuarioCreate, session: Session = Depends(get_session)): 
    return auth_service.registrar_usuario(session, dados) 

#/login usa OAuth2PasswordRequestForm, não um schema nosso (é o formato padrão que o FastAPI espera, e é o que faz o botão 'Authorize' do Swagger funcionar direitinho)
@router.post("/login", response_model=Token) 
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)): 
    
    usuario = auth_service.autenticar_usuario(session, form.username, form.password) #form.username é na verdade o email (o OAuth2 chama de 'username' por padrão, mesmo quando o campo é um email)
    token = criar_access_token({"sub": usuario.email}) 
    return Token(access_token=token)

@router.get("/me", response_model=UsuarioRead) 
def perfil(usuario_logado: 
    Usuario = Depends(get_current_user)): 
    return usuario_logado