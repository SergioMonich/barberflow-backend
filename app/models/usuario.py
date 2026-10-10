from datetime import datetime, timezone
from typing import Optional 
from sqlmodel import SQLModel, Field 

#modelando a tabela usuario
class Usuario(SQLModel, table=True): 
    
    id: Optional[int] = Field(default=None, primary_key=True) #Optional[int] com default=None no id é porque o banco gera esse valor sozinho (auto-incremento) — nunca vai preencher o id manualmente
    nome: str 
    email: str = Field(unique=True, index=True) 
    senha_hash: str 
    tipo: str = Field(default="dono") 
    criado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))