from pydantic import BaseModel, EmailStr 

#UsuarioCreate é o que a pessoa envia no registro (senha em texto puro, ainda sem hash)
class UsuarioCreate(BaseModel): 
    
    nome: str 
    email: EmailStr 
    senha: str
    nome_barbearia: str 

#UsuarioRead é o que a API devolve (não tem senha nem senha_hash, isso nunca deve sair da API)  
class UsuarioRead(BaseModel): 

    id: int 
    nome: str 
    email: str 
    tipo: str 
    
class Token(BaseModel): 

    access_token: str 
    token_type: str = "bearer"