from datetime import datetime 
from typing import Optional 
from sqlmodel import SQLModel, Field 

#modelando a tabela cleinte
class Cliente(SQLModel, table=True): 
    id: Optional[int] = Field(default=None, primary_key=True) #Optional[int] com default=None no id é porque o banco gera esse valor sozinho (auto-incremento) — nunca vai preencher o id manualmente
    barbearia_id: int = Field(foreign_key="barbearia.id") 
    nome: str 
    telefone: Optional[str] = None 
    email: Optional[str] = None 
    observacoes: Optional[str] = None 
    criado_em: datetime = Field(default_factory=datetime)