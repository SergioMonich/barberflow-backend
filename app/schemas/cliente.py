from typing import Optional 
from pydantic import BaseModel, ConfigDict 

#ClienteCreate não tem barbearia_id pois isso vem do usuário logado, nunca do corpo da requisição (senão alguém poderia criar clientes em barbearias de outras pessoas)
class ClienteCreate(BaseModel): 
    
    nome: str 
    telefone: Optional[str] = None 
    email: Optional[str] = None 
    observacoes: Optional[str] = None 
    

class ClienteRead(BaseModel): 
    
    id: int 
    barbearia_id: int 
    nome: str 
    telefone: Optional[str] = None 
    email: Optional[str] = None 
    observacoes: Optional[str] = None 
    
#ClienteUpdate tem tudo opcional, pra permitir atualizar só um campo por vez sem precisar reenviar os outros   
class ClienteUpdate(BaseModel): 
    
    nome: Optional[str] = None 
    telefone: Optional[str] = None 
    email: Optional[str] = None 
    observacoes: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={"examples": [{"telefone": "44999999999"}]})