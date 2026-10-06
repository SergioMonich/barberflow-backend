from datetime import datetime, timedelta, timezone 
from passlib.context import CryptContext 
from jose import jwt 
from app.core.config import settings 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 

#hash_senha e verificar_senha cuidam da senha (boa pratica: nunca guardamos texto puro, só o hash)
def hash_senha(senha: str) -> str:

    return pwd_context.hash(senha) 

def verificar_senha(senha: str, senha_hash: str) -> bool: 

    return pwd_context.verify(senha, senha_hash) 

def criar_access_token(dados: dict) -> str: 

    expira_em = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes) 
    payload = dados.copy() 
    payload.update({"exp": expira_em}) 
    
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")