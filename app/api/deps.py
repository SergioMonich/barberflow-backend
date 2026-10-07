from fastapi import Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordBearer 
from jose import JWTError, jwt 
from sqlmodel import Session 
from app.core.config import settings 
from app.db.session import get_session 
from app.models.usuario import Usuario 
from app.repositories import usuario_repository 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") #diz ao Swagger onde fica a rota de login

#qualquer rota que colocar Depends(get_current_user) só executa se o token for válido e recebe de volta o objeto Usuario logado, pronto pra usar
def get_current_user( 
        
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session),

) -> Usuario:
    
    credenciais_invalidas = HTTPException( 

        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Nao foi possivel validar as credenciais", 
        headers={"WWW-Authenticate": "Bearer"},

    ) 

    try: 

        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"]) 
        email: str | None = payload.get("sub") 
        if email is None: 
            raise credenciais_invalidas 
        
    except JWTError: 

        raise credenciais_invalidas 
    
    usuario = usuario_repository.buscar_por_email(session, email) 
    if usuario is None: 

        raise credenciais_invalidas 
    
    return usuario